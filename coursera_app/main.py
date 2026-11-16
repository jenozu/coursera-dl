"""FastAPI application factory (roadmap 5.1).

create_app(): include routers from ``coursera_app.api``, add middleware (Host check,
launch token, no CORS, CSP + nosniff headers, reject cross-origin POST), mount ``web/``.
"""

from __future__ import annotations


def create_app(*, token: str, port: int):
    raise NotImplementedError("roadmap 5.1")
