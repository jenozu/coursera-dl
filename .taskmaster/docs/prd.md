# Coursera Downloader (local course-material manager)

## Goal
A single user on Windows wants a reliable, local download manager for Coursera course material **their own account is enrolled in**. They open a browser page on their own machine, connect using their existing browser login, pick a course and content types, and watch downloads progress, cancel, retry and resume. Done means: repeat and partial downloads work, failures are reported honestly, nothing is reachable from the network, and no secret is ever stored or logged. The current Streamlit app is replaced by a FastAPI backend with a plain HTML/CSS/JS front end.

Source of findings: `docs/audit/AUDIT_REPORT.md` (IDs C-1, H-1 …). Design: `docs/audit/ARCHITECTURE_RECOMMENDATION.md`. Detailed task seeds: `docs/audit/IMPROVEMENT_ROADMAP.md`.

## Non-goals
- No bypassing of Coursera authentication, enrollment checks, paywalls or DRM. Only content the signed-in account can already open.
- No credentials storage, no username/password login, no account creation.
- No cloud, hosting, multi-user mode, remote access or accounts of our own.
- No paid APIs, subscriptions, CDNs, analytics or telemetry.
- No front-end framework or build step (no React/Vue/npm toolchain), no Celery/Redis/queues, no ORM.
- No desktop-app shell (Electron/Tauri/Qt) in v1.
- No scheduling, notifications, themes, drag-reorder, pause (cancel + resume covers it).
- No quizzes/notebooks/graded-assignment downloads unless the engine already supports them.
- No Chrome support in v1 (Firefox, Edge, Brave only), no macOS/Linux packaging (code stays portable, only Windows is verified).

## Success criteria
1. Downloading a course's videos, then the same course's PDFs, produces both sets (audit C-1 fixed, regression-tested).
2. A job with any failed file ends as `done_with_errors` and the UI names the failed files (H-1).
3. `netstat`/startup log shows the server bound to `127.0.0.1` only; requests with a foreign `Host`, missing token or foreign `Origin` are rejected (H-2).
4. `pip install -r requirements.txt` on a clean Python 3.11 or 3.12 virtualenv yields a working app; no `coursera-dl` legacy package (H-3).
5. Cancel stops a download within one chunk; killing the process mid-download and restarting shows the job as `interrupted` and resume completes the file byte-identically.
6. A network outage is shown as a network error, never as "session expired" (M-2); an expired session is detected before a job starts, even for previously crawled courses.
7. No cookie, CAUTH value or signed-URL query string appears in logs, the database, API responses or test output.
8. Full test suite passes in CI on Windows and Linux (Python 3.11, 3.12) using only the local fake server and sample fixtures; at least 80% coverage of `coursera_app/` excluding `web/`.
9. A new user can follow the README on clean Windows, connect, download a course they are enrolled in (manual check, `docs/LIVE_CHECKLIST.md`).

## Capabilities

### Session
- Connect from browser: read Coursera cookies from Firefox, Edge or Brave via `rookiepy`; keep them in memory only.
- Manual CAUTH fallback.
- Session check: returns valid / expired / network_error before each job and on demand.

### Course discovery
- List enrolled courses via the memberships endpoint (one `requests` call).
- Accept a pasted course URL or slug (validated).
- Refresh a course's cached structure on demand.

### Download jobs
- Crawl + gather through `dl_coursera` (pinned `==1.0.1`), our own fetch loop for the files.
- Content types: video, subtitle, pdf, reading/html, other. Explicit extension table.
- Fetch loop: timeouts, `.part` files with atomic rename, skip complete files, `Range` resume, backoff with jitter, `Retry-After` on 429, no retry on 401/403/404, cancel between chunks.
- Job states: queued, crawling, downloading, done, done_with_errors, failed, cancelled, interrupted. One job and one file at a time by default.
- Retry failed items; resume interrupted jobs.

### Web interface
- Single page: auth status header, add course, active/queued downloads with per-file progress, history, activity log, minimal settings (download folder, default types).
- Live progress by Server-Sent Events (snapshot on connect, then deltas).
- Responsive 360 px to desktop, keyboard accessible, no external requests.

### Storage
- SQLite (`data/app.db`): jobs, items, events. JSON settings (`data/settings.json`), `COURSERA_DOWNLOAD_DIR` env override.
- Files under `<download_dir>/<slug>/…` with sanitized, length-limited Windows-safe names.

### Security
- Bind `127.0.0.1` only; Host-header allowlist; per-launch token; no CORS; CSP and `nosniff`; slug validation and path containment; secret redaction in logs; 0600 temp cookie file removed after every job and swept at startup.

## Structure
```
run.py                         launcher: server on 127.0.0.1, open browser with token
coursera_app/main.py           app factory + middleware          <- Security, Web interface
coursera_app/api/              REST + SSE routes                  <- Web interface
coursera_app/services/         auth, course, download (no web imports) <- Session, Discovery, Jobs
coursera_app/engine.py         dl_coursera adapter (crawl+gather+classify) <- Download jobs
coursera_app/downloader.py     fetch loop                         <- Download jobs
coursera_app/jobs.py, db.py, schema.sql   job manager + SQLite    <- Download jobs, Storage
coursera_app/settings.py, logging_setup.py, security.py, errors.py   <- Storage, Security
coursera_app/browser_auth.py   existing, kept                     <- Session
coursera_app/web/              index.html, app.css, app.js
tests/                         unit, integration, api, fake_coursera.py, fixtures
```
The scaffold with stubs and skipped acceptance tests already exists on branch `rebuild/fastapi`.

## Dependency order
1. Foundation (no deps): `errors`, `security`, `settings`, `logging_setup`.
2. `browser_auth` (exists), `engine` (needs security), `downloader` (needs errors).
3. `db` + `schema.sql`, then `jobs` (needs db, engine, downloader).
4. `services/*` (need 1–3).
5. `api/*` and `main` (need services, security).
6. `web/*` (needs API contract).
7. Cutover: remove Streamlit app and legacy `coursera-dl` last.
No cycles; `services/` never imports FastAPI or Streamlit.

## Phases
- **Phase 0 Prep:** README corrected, CI green, fake server and fixtures usable. Exit: `scripts/dev.ps1` passes; skipped tests are the only skips.
- **Phase 1 Critical fixes on the existing app (M1):** C-1, H-1, H-2, slug validation, with regression tests. Exit: Streamlit app downloads twice with different selections, reports failures, binds to localhost.
- **Phase 2 Backend core (M2):** legacy package removed, typed errors, redacted logging, settings, safe paths, cookie handling. Exit: app and tests run without `coursera-dl`.
- **Phase 3 Download engine (M3):** fetch loop, job manager, SQLite, cancel, cache refresh, classification. Exit: end-to-end integration test against the fake server passes.
- **Phase 4 Auth hardening (M4):** typed session check, pre-flight check, expiry states. Exit: all auth-service tests pass.
- **Phase 5 API (M5):** FastAPI app, security middleware, routes, SSE. Exit: API security tests pass; `run.py` serves the API.
- **Phase 6 Web UI (M6):** single-page UI. Exit: manual UI checklist passes against the fake server.
- **Phase 7 Cutover and docs (M7):** delete Streamlit and legacy files, final README and `docs/ARCHITECTURE.md`, engine contract test. Exit: CI green, no `streamlit` or `coursera` imports.
- **Phase 8 Live verification and release (M8):** Windows checklist, launcher, tagged release. Needs the user.

## Test strategy
- `pytest` with markers `unit`, `integration`, `api`; run with `.\scripts\dev.ps1` (ruff + pytest) or `python -m pytest -q`.
- Skipped tests in `tests/` are the acceptance criteria; each task un-skips its tests, then implements.
- Only the local fake Coursera server and hand-made fixtures; never live Coursera, never real course content.
- Critical regression tests: C-1, H-1, M-6 slug traversal, expired-vs-network error, cookie-file cleanup, cancel, resume, log redaction.

## Architecture and stack
- Python 3.11/3.12, FastAPI + uvicorn (required by user), `requests`, `rookiepy`, `dl-coursera==1.0.1` (crawl+gather only), stdlib `sqlite3`, `threading`. Front end: plain HTML, modern CSS, vanilla JS (required by user).
- SSE over WebSockets (one-way, built into browsers). In-process job manager over a worker/queue (single user).
- Rejected: Streamlit (rerun model, binds all interfaces), Electron/Tauri/Qt (heavy), Celery/Redis (overkill), ORM (unneeded), legacy `coursera-dl` (unmaintained, `distutils`).
- Dev tooling: `pytest`, `pytest-cov`, `responses`, `httpx`, `ruff`, `pip-audit`.

## Risks and open questions
- Coursera's endpoints are unofficial and can change; keep the engine behind `engine.py`, pin its version, add a contract check.
- `rookiepy` on Windows with Edge/Brave may need Administrator or fail on newer browser encryption: unverified until M8; manual CAUTH remains the fallback.
- Whether signed asset URLs expire while queued: unverified; design re-gathers on 403.
- Which cookies beyond CAUTH the engine needs: try CAUTH only, widen only if live testing proves it necessary.
- Whether `dl_coursera` can honor resolution/subtitle-language: unknown, so those options are out of v1 scope.
- Windows path length (260): downloader must shorten names.

## Decision log
- 2026-11-09: Replace Streamlit with FastAPI + vanilla HTML/JS (option B) because background jobs, cancel and a persistent queue fit poorly with Streamlit reruns (audit H-5). Affects phases 5–7.
- 2026-11-09: Keep Streamlit app working until Phase 7; fix C-1/H-1/H-2 in it first (Phase 1).
- 2026-11-09: Own the download step instead of `dl_coursera_run.download()` because its hidden failed-list file overrides selection (C-1).
- 2026-11-09: Remove legacy `coursera-dl`; list courses with one memberships request. (default, user may override)
- 2026-11-09: Branch `rebuild/fastapi`, MIT license, JSON settings only, Python 3.11 + 3.12, PowerShell scripts only. (user "go" defaults)
