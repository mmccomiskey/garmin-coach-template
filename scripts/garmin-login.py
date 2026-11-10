# /// script
# requires-python = ">=3.10"
# dependencies = ["garminconnect==0.3.2"]
# ///
"""Browser-based Garmin login for the running coach.

Serves a one-page login form on 127.0.0.1, sends the athlete's credentials
straight to Garmin, and saves OAuth tokens to ~/.garminconnect, the same
place `garmin-mcp-auth` uses. The AI only starts this script and reads the
one-line result; the password never appears in arguments, env vars, or
output. Mirrors the login flow in garmin_mcp/auth_cli.py at the pinned
version (garminconnect 0.3.2).

Run:  uv run scripts/garmin-login.py [--force] [--no-browser]
Exit: 0 connected, 1 login failed, 2 timed out or stopped.
"""

import argparse
import html
import io
import os
import secrets
import signal
import sys
import threading
import time
import webbrowser
from contextlib import redirect_stderr
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

IDLE_TIMEOUT = 15 * 60
# A typo deserves one more try; more than that risks Garmin's rate limit.
MAX_PASSWORD_TRIES = 2


def token_dir() -> str:
    env = os.getenv("GARMINTOKENS")
    # A long GARMINTOKENS value is inline JSON, not a path.
    if env and len(env) <= 512:
        return os.path.expanduser(env)
    return os.path.expanduser("~/.garminconnect")


def secure(path: str) -> None:
    os.chmod(path, 0o700)
    for entry in os.scandir(path):
        if entry.is_file():
            os.chmod(entry.path, 0o600)


def saved_login_works(path: str) -> str | None:
    """Return the account name if saved tokens authenticate, else None."""
    if not os.path.isfile(os.path.join(path, "garmin_tokens.json")):
        return None
    try:
        with redirect_stderr(io.StringIO()):
            g = Garmin()
            g.login(path)
            return g.get_full_name() or g.display_name or "your account"
    except Exception:
        return None


def say(msg: str) -> None:
    print(msg, flush=True)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Connect Garmin</title>
<style>
:root {{ --bg:#f3f5f7; --card:#fff; --fg:#17202a; --muted:#5b6876;
  --line:#d5dbe1; --accent:#0a6ebd; --bad:#b3261e; --good:#1e7a3a; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#10151a; --card:#182028;
  --fg:#e6ebf0; --muted:#9aa7b4; --line:#2d3946; --accent:#5aa9e6;
  --bad:#f2867e; --good:#6fcf8f; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; min-height:100vh; display:grid; place-items:center;
  background:var(--bg); color:var(--fg); padding:16px;
  font:16px/1.5 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
main {{ width:100%; max-width:400px; background:var(--card);
  border:1px solid var(--line); border-radius:12px; padding:28px; }}
h1 {{ font-size:1.35rem; margin:0 0 6px; }}
p {{ margin:0 0 16px; color:var(--muted); }}
label {{ display:block; font-weight:600; margin:14px 0 6px; }}
input {{ width:100%; font:inherit; padding:10px 12px; color:var(--fg);
  background:var(--bg); border:1px solid var(--line); border-radius:8px; }}
input:focus {{ outline:2px solid var(--accent); outline-offset:1px; }}
button {{ width:100%; margin-top:20px; font:inherit; font-weight:600; color:#fff;
  background:var(--accent); border:0; border-radius:8px; padding:12px;
  cursor:pointer; }}
button:disabled {{ opacity:.6; cursor:wait; }}
.msg {{ padding:10px 12px; border-radius:8px; margin:0 0 16px;
  border:1px solid currentColor; }}
.bad {{ color:var(--bad); }} .good {{ color:var(--good); }}
.fine {{ font-size:.85rem; margin:18px 0 0; }}
</style></head><body><main>{body}</main>
<script>
for (const f of document.querySelectorAll("form")) f.addEventListener(
  "submit", () => {{ const b = f.querySelector("button");
  b.disabled = true; b.textContent = "Connecting to Garmin..."; }});
</script></body></html>"""

FINE_PRINT = (
    '<p class="fine">Your password goes from this page straight to Garmin. '
    "Your AI coach never sees it, and nothing is stored except Garmin's "
    "login token on this computer.</p>"
)


def login_form(token: str, error: str = "") -> str:
    err = f'<div class="msg bad">{html.escape(error)}</div>' if error else ""
    return f"""<h1>Connect your Garmin account</h1>
<p>Sign in with the email and password you use for Garmin Connect.</p>
{err}<form method="post" action="/login">
<input type="hidden" name="t" value="{token}">
<label for="email">Email</label>
<input id="email" name="email" type="email" autocomplete="username"
  required autofocus>
<label for="password">Password</label>
<input id="password" name="password" type="password"
  autocomplete="current-password" required>
<button type="submit">Connect Garmin</button></form>{FINE_PRINT}"""


def mfa_form(token: str, error: str = "") -> str:
    err = f'<div class="msg bad">{html.escape(error)}</div>' if error else ""
    return f"""<h1>Enter your Garmin code</h1>
<p>Garmin just sent a verification code to your email or phone.</p>
{err}<form method="post" action="/mfa">
<input type="hidden" name="t" value="{token}">
<label for="code">Verification code</label>
<input id="code" name="code" inputmode="numeric" autocomplete="one-time-code"
  required autofocus>
<button type="submit">Finish connecting</button></form>{FINE_PRINT}"""


def done_page(ok: bool, text: str) -> str:
    cls = "good" if ok else "bad"
    title = "You're connected" if ok else "That didn't work"
    return (
        f'<h1>{title}</h1><div class="msg {cls}">{html.escape(text)}</div>'
        "<p>You can close this tab and go back to your AI coach.</p>"
    )


class Login:
    """State for one login attempt, shared by request handlers."""

    def __init__(self, path: str):
        self.path = path
        self.token = secrets.token_urlsafe(24)
        self.lock = threading.Lock()
        self.garmin: Garmin | None = None
        self.mfa_state = None
        self.tries = 0
        self.result: tuple[int, str] | None = None
        self.last_activity = time.monotonic()

    def finish(self, code: int, msg: str) -> None:
        self.result = (code, msg)

    def save(self) -> str:
        os.makedirs(self.path, exist_ok=True)
        self.garmin.client.dump(self.path)
        secure(self.path)
        # return_on_mfa skips the profile check, so confirm the saved
        # tokens actually work rather than trusting the dump.
        name = saved_login_works(self.path)
        if not name:
            raise RuntimeError("tokens saved but Garmin rejected them")
        return name

    def submit_password(self, email: str, password: str) -> tuple[str, str]:
        """Return (page_kind, message): 'mfa', 'retry', or 'done'."""
        self.tries += 1
        try:
            with redirect_stderr(io.StringIO()):
                self.garmin = Garmin(email=email, password=password,
                                     return_on_mfa=True)
                first, second = self.garmin.client.login(
                    email, password, return_on_mfa=True)
            if first == "needs_mfa":
                self.mfa_state = second
                return "mfa", ""
            name = self.save()
            self.finish(0, f"SUCCESS: connected as {name}")
            return "done", f"Garmin is connected for {name}."
        except GarminConnectTooManyRequestsError:
            return self._fail_hard(
                "RATE_LIMITED: Garmin asked us to slow down",
                "Garmin is limiting login attempts right now. Wait at least "
                "an hour, then ask your coach to try again.")
        except GarminConnectAuthenticationError:
            if self.tries < MAX_PASSWORD_TRIES:
                return "retry", ("Garmin didn't accept that email and "
                                 "password. Check them and try once more.")
            return self._fail_hard(
                "FAILED: Garmin rejected the email or password twice",
                "Garmin didn't accept the email and password. To avoid "
                "getting locked out, wait an hour before trying again. You "
                "can check your password at connect.garmin.com.")
        except (GarminConnectConnectionError, RuntimeError, OSError) as e:
            return self._fail_hard(
                f"FAILED: {type(e).__name__}",
                "Something went wrong talking to Garmin. Wait a bit, then "
                "ask your coach to try again.")

    def submit_mfa(self, code: str) -> tuple[str, str]:
        try:
            with redirect_stderr(io.StringIO()):
                self.garmin.resume_login(self.mfa_state, code.strip())
            name = self.save()
            self.finish(0, f"SUCCESS: connected as {name}")
            return "done", f"Garmin is connected for {name}."
        except GarminConnectTooManyRequestsError:
            return self._fail_hard(
                "RATE_LIMITED: Garmin asked us to slow down",
                "Garmin is limiting login attempts right now. Wait at least "
                "an hour, then ask your coach to try again.")
        except Exception as e:
            return self._fail_hard(
                f"FAILED: verification code step ({type(e).__name__})",
                "That code didn't work. Codes expire quickly. Wait a few "
                "minutes, then ask your coach to start the login again.")

    def _fail_hard(self, log: str, page: str) -> tuple[str, str]:
        self.finish(1, log)
        return "failed", page


def make_handler(state: Login, port: int):
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep form data out of any output
            pass

        def _send(self, status: int, body: str) -> None:
            data = PAGE.format(body=body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _host_ok(self) -> bool:
            # Blocks DNS-rebinding pages that resolve to 127.0.0.1.
            return self.headers.get("Host", "") in allowed_hosts

        def do_GET(self):
            if not self._host_ok():
                return self._send(403, "<h1>Not allowed</h1>")
            q = parse_qs(urlparse(self.path).query)
            if urlparse(self.path).path != "/" or \
                    q.get("t", [""])[0] != state.token:
                return self._send(404, "<h1>Not found</h1><p>Use the link "
                                  "your coach opened for you.</p>")
            state.last_activity = time.monotonic()
            if state.result:
                return self._send(200, done_page(
                    state.result[0] == 0, "This login has already finished."))
            if state.mfa_state is not None:
                return self._send(200, mfa_form(state.token))
            self._send(200, login_form(state.token))

        def do_POST(self):
            if not self._host_ok():
                return self._send(403, "<h1>Not allowed</h1>")
            origin = self.headers.get("Origin")
            if origin and urlparse(origin).netloc not in allowed_hosts:
                return self._send(403, "<h1>Not allowed</h1>")
            length = min(int(self.headers.get("Content-Length") or 0), 8192)
            form = parse_qs(self.rfile.read(length).decode())
            field = lambda k: form.get(k, [""])[0]
            if not secrets.compare_digest(field("t"), state.token):
                return self._send(403, "<h1>Not allowed</h1>")
            state.last_activity = time.monotonic()

            with state.lock:
                if state.result:
                    return self._send(200, done_page(
                        state.result[0] == 0,
                        "This login has already finished."))
                route = urlparse(self.path).path
                if route == "/login" and state.mfa_state is None:
                    kind, msg = state.submit_password(
                        field("email").strip(), field("password"))
                elif route == "/mfa" and state.mfa_state is not None:
                    kind, msg = state.submit_mfa(field("code"))
                else:
                    return self._send(400, "<h1>Unexpected request</h1>")

            if kind == "mfa":
                say("WAITING: Garmin sent a verification code")
                self._send(200, mfa_form(state.token))
            elif kind == "retry":
                say("RETRY: Garmin rejected the email or password once")
                self._send(200, login_form(state.token, msg))
            else:
                self._send(200, done_page(kind == "done", msg))

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--force", action="store_true",
                    help="log in again even if a saved login works")
    ap.add_argument("--no-browser", action="store_true",
                    help="print the link instead of opening a browser")
    args = ap.parse_args()

    path = token_dir()
    if not args.force:
        name = saved_login_works(path)
        if name:
            say(f"ALREADY_CONNECTED: saved Garmin login works for {name}")
            return 0

    state = Login(path)
    server = ThreadingHTTPServer(("127.0.0.1", 0), None)
    port = server.server_address[1]
    server.RequestHandlerClass = make_handler(state, port)
    url = f"http://127.0.0.1:{port}/?t={state.token}"

    def stop(*_):
        if state.result is None:
            state.finish(2, "STOPPED: login was cancelled")
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    threading.Thread(target=server.serve_forever, daemon=True).start()
    if args.no_browser or not webbrowser.open(url):
        say(f"OPEN_THIS: {url}")
    say("WAITING: login page is open in the browser")

    while state.result is None:
        if time.monotonic() - state.last_activity > IDLE_TIMEOUT:
            state.finish(2, "TIMED_OUT: no login within 15 minutes")
            break
        time.sleep(0.5)
    time.sleep(1)  # let the final page finish sending
    server.shutdown()

    code, msg = state.result
    say(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
