"""REST routes under /api (roadmap 5.2, 5.3). Each module exposes ``router``.

Planned routes:
  auth.py       GET /auth/status, POST /auth/connect, POST /auth/disconnect
  courses.py    GET /courses
  downloads.py  POST /downloads, GET /downloads, POST /downloads/{id}/cancel, /retry
  events.py     GET /events (SSE: snapshot, then deltas)
  settings.py   GET/PUT /settings
  logs.py       GET /logs
Errors: {"error": {"code", "message", "hint"}} from coursera_app.errors.
"""
