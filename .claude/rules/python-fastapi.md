---
paths:
  - "coursera_app/**/*.py"
  - "tests/**/*.py"
  - "run.py"
---

# Python rules (coursera_app)

- Layout: `api/` routes (thin), `services/` logic (never imports FastAPI or Streamlit), `engine.py` is the only
  module that touches `dl_coursera`, `downloader.py` is the fetch loop, `jobs.py`/`db.py`/`schema.sql` hold job state.
- Use `.venv/Scripts/python.exe` (Git Bash) or `.\.venv\Scripts\python.exe`, never the system python. Pin a new
  dependency only when a roadmap task names it.
- Type hints on new functions. Pydantic models for every request and response body.
- stdlib `sqlite3` with bound parameters only (no string-built SQL, no ORM). Schema lives in `schema.sql`.
- `logging`, not `print`. Never log cookies, CAUTH values, or URLs with a query string; go through the redaction helpers.
- Every user-supplied slug/path is validated and checked to stay inside the download dir before touching disk.
- Typed errors from `errors.py`; a network failure is never reported as "session expired".
- Tests: pytest, markers `unit`/`integration`/`api`, only `tests/fake_coursera.py` and `tests/fixtures/`. Never live Coursera.
- Keep `requirements*.txt` UTF-8 (Windows editors sometimes save UTF-16, which breaks pip).
