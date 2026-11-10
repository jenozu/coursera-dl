"""Local fake Coursera server for tests (roadmap 7.1).

Serves, on 127.0.0.1 and a random port:
  GET /memberships        -> fixtures/sample_course/memberships.json (401 if no CAUTH cookie)
  GET /files/<name>       -> small files from fixtures/sample_course/files/
Behaviors to add as the downloader is built (roadmap 4.1): 429 with Retry-After, 5xx then success,
mid-body disconnect, slow response, Range/206 support.
All content is hand-made sample data, never real course material.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures" / "sample_course"


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silence test output
        pass

    def _send(self, status: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/memberships"):
            if "CAUTH=" not in (self.headers.get("Cookie") or ""):
                self._send(401, b'{"errorCode": "Not Authorized"}')
                return
            self._send(200, (FIXTURES / "memberships.json").read_bytes())
        elif self.path.startswith("/files/"):
            target = (FIXTURES / "files" / Path(self.path).name).resolve()
            if target.is_file() and (FIXTURES / "files").resolve() in target.parents:
                self._send(200, target.read_bytes(), "application/octet-stream")
            else:
                self._send(404, b"{}")
        else:
            self._send(404, b"{}")


class FakeCoursera:
    def __init__(self) -> None:
        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}"

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=5)
        assert json is not None  # json kept imported for future endpoints
