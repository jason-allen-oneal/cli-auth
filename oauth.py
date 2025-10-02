import os, base64, hashlib, socket, urllib.parse, http.server, threading
from storage import now

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def gen_code_verifier() -> str:
    return b64url(os.urandom(32))

def gen_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return b64url(digest)

class CodeHandler(http.server.BaseHTTPRequestHandler):
    STATE = None
    RESULT = {"code": None, "error": None}
    DONE_EVENT = None

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path != "/callback":
            self.send_response(404); self.end_headers(); return
        qs = urllib.parse.parse_qs(u.query)
        code = qs.get("code", [None])[0]
        err  = qs.get("error", [None])[0]
        if err:
            CodeHandler.RESULT["error"] = err
        else:
            CodeHandler.RESULT["code"] = code
        if CodeHandler.DONE_EVENT:
            CodeHandler.DONE_EVENT.set()
        self.send_response(200); self.end_headers()
        self.wfile.write(b"You may close this window now.")

def find_free_port(preferred: int = 53682) -> int:
    try:
        with socket.socket() as s:
            s.bind(("127.0.0.1", preferred))
            return preferred
    except OSError:
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]
