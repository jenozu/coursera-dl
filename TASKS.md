# Coursera Downloader task checklist

Generated from `.taskmaster/tasks/tasks.json` (the source of truth). Never edit by hand; regenerate with
`python .taskmaster/render_tasks_md.py`.

**Progress: 1/39 tasks done.**

## Phase 0 - Prep

- [x] **1. Adopt master-harness and finish M0 repo prep**\
  Harness installed; README/MASTER_PLAN corrected, CI green, fake server and fixtures in place (roadmap 1.5, 1.4, 7.1).\
  _Test:_ python -m pytest -q tests/unit/test_fake_server.py

## Phase 1 - Critical fixes

- [ ] **2. Own the download step in downloader.py (roadmap 1.1, C-1, H-1)** _(after 1)_\
  Stop calling dl_coursera_run.download(); our downloader returns per-item results done/skipped/failed and ignores the engine failed-list file.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_downloader.py tests/test_download_engine.py
- [ ] **3. Report download outcomes in the Streamlit UI (roadmap 1.2)** _(after 2)_\
  Replace 'Finished' with 'Downloaded X, skipped Y, failed Z' and list failed files with reasons; rename download_tasks to selected_tasks.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests
- [ ] **4. Bind Streamlit to localhost, disable usage stats (roadmap 1.3, H-2)** _(after 1)_\
  Commit .streamlit/config.toml (address 127.0.0.1, gatherUsageStats=false), make scripts/run.ps1 use it, document it.\
  _Test:_ Start app as scripts/run.ps1 does and confirm the log shows no Network URL; .venv/Scripts/python.exe -m pytest -q tests
- [ ] **5. Validate course slugs and constrain output paths (roadmap 1.6, M-6)** _(after 1)_\
  validate_slug() (^[a-z0-9][a-z0-9-]{0,127}$) plus resolved-path containment, called from download_course().\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_security.py
- [ ] **6. Phase 1 gate: ruff and pytest pass** _(after 2, 3, 4, 5)_\
  Free script gate before the phase PR.\
  _Test:_ python .taskmaster/run_checks.py run --only <id>

## Phase 2 - Backend core

- [ ] **7. Engine adapter, services layer and typed errors (roadmap 2.1)** _(after 6)_\
  Move crawl/gather into engine.py, services/ with no Streamlit/FastAPI imports, errors.py hierarchy (AuthExpired, CourseNotFound, NetworkError, DiskError, RateLimited).\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_engine_new.py tests/unit/test_errors.py
- [ ] **8. Remove legacy coursera-dl; list courses via memberships endpoint (roadmap 2.2, M-1)** _(after 7)_\
  One requests call with timeouts, status handling and JSON-shape checks; delete coursera-dl from setup, README and requirements.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_auth_service.py
- [ ] **9. Logging with secret redaction (roadmap 2.3)** _(after 7)_\
  Rotating file log in data/logs/ with a filter masking CAUTH, cookie values and signed-URL query strings.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_logging_redaction.py
- [ ] **10. Settings module (roadmap 2.4)** _(after 7)_\
  JSON settings data/settings.json (download dir, default types), COURSERA_DOWNLOAD_DIR override, validate directory is writable.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_settings.py
- [ ] **11. Minimize and protect cookies (roadmap 3.3)** _(after 7)_\
  Cookies in memory only, CAUTH-only first; temp cookie file under data/tmp with 0600, removed after success, error and cancel, swept at startup.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_auth_service.py tests/unit/test_security.py
- [ ] **12. Safe Windows-safe file naming (roadmap 4.2)** _(after 7)_\
  Sanitize every path segment (reserved names, trailing dots, control chars), cap lengths, contain under root, de-duplicate.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit
- [ ] **13. Phase 2 gate: ruff and pytest pass** _(after 7, 8, 9, 10, 11, 12)_\
  Free script gate before the phase PR.\
  _Test:_ python .taskmaster/run_checks.py run --only <id>

## Phase 3 - Download engine

- [ ] **14. Robust fetch loop (roadmap 4.1)** _(after 13)_\
  Timeouts, .part streaming with atomic rename, skip complete files, Range resume, size check, backoff with jitter, Retry-After on 429, no retry on 401/403/404.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_downloader.py
  - [ ] 14.1 Streaming to .part, atomic rename, skip complete files
  - [ ] 14.2 Range resume and Content-Length size check
  - [ ] 14.3 Backoff with jitter, Retry-After on 429, no retry on 401/403/404, timeouts
- [ ] **15. Job manager and SQLite schema (roadmap 2.5)** _(after 14)_\
  jobs.py worker thread with cancel Event and status transitions; db.py jobs/items/events; running jobs become interrupted at startup; one job per course.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_jobs_db.py
- [ ] **16. Cancel and cleanup (roadmap 4.3)** _(after 15)_\
  Cancel exits between chunks, leaves .part for resume, marks items cancelled, no threads left.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_jobs_db.py tests/unit/test_downloader.py
- [ ] **17. Cache refresh with JSON structure (roadmap 4.4)** _(after 13)_\
  Refresh discards cached structure; store JSON not pickle; re-gather stale tasks.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_engine_new.py
- [ ] **18. Tighten content-type classification (roadmap 4.5)** _(after 13)_\
  Explicit documented extension table: video, subtitle, pdf, reading/html, other.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_engine_new.py
- [ ] **19. End-to-end test against the fake server** _(after 15, 16, 17, 18)_\
  crawl, gather, download, verify files in under 30 s.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/integration
- [ ] **20. Phase 3 gate: ruff and pytest pass** _(after 14, 15, 16, 17, 18, 19)_\
  Free script gate before the phase PR.\
  _Test:_ python .taskmaster/run_checks.py run --only <id>

## Phase 4 - Auth hardening

- [ ] **21. Typed session check (roadmap 3.1, M-2)** _(after 20)_\
  check_session() returns valid | expired | network_error; run on connect, before each job, on demand, also for cached courses.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_auth_service.py
- [ ] **22. Drop dependence on the engine canary course (roadmap 3.2)** _(after 21)_\
  Map engine CookiesExpiredException to AuthExpired with the app's own guidance (no cookies.txt mention).\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_auth_service.py tests/unit/test_engine_new.py
- [ ] **23. Backend session lifecycle states (roadmap 3.5)** _(after 21)_\
  Expiry mid-queue marks remaining jobs paused:auth and they run after reconnect. UI part is in phase 6.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/unit/test_jobs_db.py tests/unit/test_auth_service.py
- [ ] **24. Phase 4 gate: ruff and pytest pass** _(after 21, 22, 23)_\
  Free script gate before the phase PR.\
  _Test:_ python .taskmaster/run_checks.py run --only <id>

## Phase 5 - API

- [ ] **25. FastAPI shell and security middleware (roadmap 5.1)** _(after 24)_\
  create_app(); Host allowlist, per-launch token, Origin check, no CORS, CSP and nosniff; run.py binds 127.0.0.1 and opens the browser with the token.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/api/test_api_security.py
- [ ] **26. Auth and course routes (roadmap 5.2)** _(after 25)_\
  GET /api/auth/status, POST /api/auth/connect, /disconnect, GET /api/courses with typed error bodies; no cookie values in responses.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/api
- [ ] **27. Download and settings routes plus SSE (roadmap 5.3)** _(after 25)_\
  POST/GET /api/downloads, cancel, retry, GET/PUT /api/settings, GET /api/events snapshot then deltas; invalid slug returns invalid_slug.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests/api
- [ ] **28. Phase 5 gate: ruff and pytest pass** _(after 25, 26, 27)_\
  Free script gate before the phase PR.\
  _Test:_ python .taskmaster/run_checks.py run --only <id>

## Phase 6 - Web UI

- [ ] **29. Static single-page UI (roadmap 5.4)** _(after 28)_\
  Header auth status, Add Course, Downloads (active/queued/history), Log panel, Settings; plain HTML/CSS/JS, no CDN, 360 px to desktop, keyboard accessible, SSE progress.\
  _Test:_ See subtasks; manual checklist in .taskmaster/docs/manual-checks.md
  - [ ] 29.1 Page shell, auth status header, add-course panel and course list
  - [ ] 29.2 Downloads list with SSE progress, cancel and retry, history and log panel
  - [ ] 29.3 Settings panel, responsive layout (360 px), keyboard and accessibility pass
- [ ] **30. Phase 6 gate: ruff and pytest pass** _(after 29)_\
  Free script gate before the phase PR.\
  _Test:_ python .taskmaster/run_checks.py run --only <id>

## Phase 7 - Cutover and docs

- [ ] **31. Remove Streamlit and legacy files (roadmap 5.5)** _(after 30)_\
  Delete app.py, auth.py, download_engine.py, streamlit from requirements, Streamlit lines from README and .gitignore.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q tests; grep -ri streamlit requirements.txt coursera_app run.py returns nothing
- [ ] **32. CI matrix and 80% coverage (roadmap 7.3, 7.2)** _(after 31)_\
  CI green on Windows and Linux, Python 3.11 and 3.12 with ruff, pytest, pip-audit; coverage of coursera_app excluding web at least 80%.\
  _Test:_ .venv/Scripts/python.exe -m pytest -q --cov=coursera_app
- [ ] **33. Engine contract test (roadmap 8.4)** _(after 32)_\
  Test that imports dl_coursera_run and asserts the functions and signatures the adapter uses; run by scripts/check_engine.py and CI.\
  _Test:_ .venv/Scripts/python.exe scripts/check_engine.py
- [ ] **34. Final README and docs/ARCHITECTURE.md (roadmap 7.4)** _(after 31)_\
  README: install, run, authenticate, troubleshoot, security notes; ARCHITECTURE.md condensed from the recommendation; tick MASTER_PLAN.\
  _Test:_ Run every command in the README against the fake setup.
- [ ] **35. Phase 7 gate: ruff and pytest pass** _(after 31, 32, 33, 34)_\
  Free script gate before the phase PR.\
  _Test:_ python .taskmaster/run_checks.py run --only <id>

## Phase 8 - Live verification and release

- [ ] **36. Live per-browser verification on Windows (roadmap 3.4)** **[HUMAN]** _(after 35)_\
  Firefox, Edge, Brave, logged in/out, browser open/closed, admin or not; manual CAUTH fallback; record table in README.\
  _Test:_ Browser x condition table committed.
- [ ] **37. Live end-to-end checklist on one enrolled course (roadmap 8.1)** **[HUMAN]** _(after 36)_\
  Complete docs/LIVE_CHECKLIST.md: connect, list, download, repeat download, cancel, resume; sign off.\
  _Test:_ Signed-off checklist in docs/.
- [ ] **38. Launcher (roadmap 8.2)** _(after 37)_\
  scripts/run.ps1 and run.bat create the venv on first run, start the server, open the browser.\
  _Test:_ Fresh clone: double-click run.bat launches the app.
- [ ] **39. Versioning and release (roadmap 8.3)** _(after 37)_\
  __version__, CHANGELOG, tagged release with zip, upgrade notes including pinning dl-coursera.\
  _Test:_ Tag builds an artifact; upgrade notes read cleanly.
