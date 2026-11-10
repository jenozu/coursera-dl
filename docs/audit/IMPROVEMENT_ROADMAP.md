# IMPROVEMENT_ROADMAP — Coursera Downloader

Planning document only. Nothing here has been implemented. References: `AUDIT_REPORT.md` (finding IDs) and `ARCHITECTURE_RECOMMENDATION.md` (target design).

Priority key: **P0** do first, blocks everything · **P1** needed for a reliable first release · **P2** valuable, can follow · **P3** optional.

Sequencing principle: fix what is wrong (phases 1–4) before adding features (phases 5–6); keep the Streamlit app usable until the new UI covers the MVP.

Testing rule for every task: use locally created sample course data and fake servers. Do not download protected or unauthorized content.

---

## Phase 1 — Critical bug fixes

### 1.1 Own the download step (fixes C-1 and H-1)
- **Description:** Stop calling `dl_coursera_run.download()`. Add a `downloader.py` that takes the filtered task list, downloads each file, and returns per-item results (`done`, `skipped`, `failed` with a reason). Do not read or write the engine's `download.dl_tasks_failed.json`. Update `download_course()` to return counts of succeeded, skipped, failed.
- **Priority:** P0
- **Dependencies:** none
- **Expected outcome:** Repeat and partial downloads work; the summary reflects reality.
- **Acceptance criteria:**
  - Test: run 1 downloads videos, run 2 on the same course downloads PDFs; both sets exist on disk.
  - Test: a task that returns HTTP 500 three times is reported `failed`, and the summary does not say "finished" without errors.
  - Test: a stale `download.dl_tasks_failed.json` in the cache folder has no effect on which files are downloaded.
  - Existing three `crawl()` signature tests still pass.

### 1.2 Report outcomes in the UI
- **Description:** Replace "Finished / processed N" with "Downloaded X, skipped Y, failed Z" and list failed files with reasons. Rename `download_tasks` to `selected_tasks`.
- **Priority:** P0
- **Dependencies:** 1.1
- **Expected outcome:** No silent partial failures.
- **Acceptance criteria:** With one forced failure the page shows a warning state and names the failed file; with zero failures it shows success.

### 1.3 Bind to localhost and disable usage stats (fixes H-2, L-1)
- **Description:** Run with `--server.address 127.0.0.1`, set `browser.gatherUsageStats=false`. Commit a `.streamlit/config.toml` (remove `.streamlit/` from `.gitignore` for that one file) and make `scripts/run.ps1` use it. Document it.
- **Priority:** P0
- **Dependencies:** none
- **Expected outcome:** App not reachable from other machines while Streamlit remains.
- **Acceptance criteria:** On startup the log shows only `127.0.0.1`/`localhost`, no "Network URL"; a request from another host on the LAN is refused.

### 1.4 Make installation reproducible (fixes H-3)
- **Description:** One documented install command. Until 2.2 removes the legacy package, add it to `requirements.txt` in a way that avoids the `attrs` pin conflict (or install via `setup.ps1` only and make `app.py` show a clear "run setup.ps1" message on `ImportError`). Add a startup self-check.
- **Priority:** P0
- **Dependencies:** none
- **Expected outcome:** A fresh clone reaches the logged-out screen with the documented steps.
- **Acceptance criteria:** In a new virtualenv, following the README verbatim produces a running app; no `ModuleNotFoundError`.

### 1.5 Correct the README and MASTER_PLAN (fixes H-4, L-2)
- **Description:** Remove claims for features that do not exist (log viewer, retry/cancel, progress), fix "reads only CAUTH", update project structure and test sections, fix the literal `\n` in `MASTER_PLAN.md`, tick the verified Phase 1 item.
- **Priority:** P0
- **Dependencies:** none
- **Expected outcome:** Documentation matches behavior.
- **Acceptance criteria:** Each README feature bullet maps to a visible control or a test.

### 1.6 Validate course slugs and constrain output paths (fixes M-6)
- **Description:** Add `validate_slug()` (`^[a-z0-9][a-z0-9-]{0,127}$`) and a path-containment check (resolved course directory must be inside the download root). Call both in `download_course()`.
- **Priority:** P0 (latent today; mandatory before any free-text slug input)
- **Dependencies:** none
- **Expected outcome:** No path escapes.
- **Acceptance criteria:** Tests reject `../x`, `a/b`, absolute paths, empty and over-long slugs; accept normal slugs.

---

## Phase 2 — Backend stabilization

### 2.1 Split the engine adapter and add a services layer
- **Description:** Move crawl/gather into `engine.py`, add `services/` (auth, courses, downloads) with no UI imports, and a typed error hierarchy (`AuthExpired`, `CourseNotFound`, `NetworkError`, `DiskError`, `RateLimited`). Stop wrapping everything in `DownloadEngineError(str(exc))`; map engine exceptions by type (`CookiesExpiredException`, `NotFoundExcepton`, `requests` errors).
- **Priority:** P1
- **Dependencies:** 1.1
- **Expected outcome:** Errors carry meaning; UI code is thin.
- **Acceptance criteria:** Unit tests map each engine exception to the right typed error and message; `services/` imports nothing from Streamlit or FastAPI.

### 2.2 Remove the legacy `coursera-dl` dependency (M-1)
- **Description:** Replace `get_session()`/`list_courses()` with a `requests` call to the memberships endpoint, with timeouts, status-code handling and JSON-shape checks. Delete `coursera-dl` from setup, README and `requirements.txt`, and drop `six`, `keyring`, `pyasn1`, `configargparse`, `attrs`, `urllib3` unless needed directly.
- **Priority:** P1
- **Dependencies:** 2.1
- **Expected outcome:** One Coursera access path; no `--no-deps` workaround; works on Python 3.12+.
- **Acceptance criteria:** `pip install -r requirements.txt` alone is sufficient; app starts on Python 3.11 and 3.12; mocked memberships replies (success, 401, 5xx, malformed JSON, empty) produce the right result or typed error; `import coursera` appears nowhere.

### 2.3 Add logging with redaction
- **Description:** Use `logging` with a rotating file in `data/logs/`; add a filter that masks `CAUTH`, cookie values and signed-URL query strings.
- **Priority:** P1
- **Dependencies:** 2.1
- **Expected outcome:** Diagnosable failures without leaking secrets.
- **Acceptance criteria:** Test logs a message containing a fake CAUTH and a signed URL and asserts neither appears in the output file.

### 2.4 Settings module
- **Description:** JSON settings (`data/settings.json`) for download directory and defaults; keep the `COURSERA_DOWNLOAD_DIR` environment variable as an override. Validate that the directory exists or can be created and is writable.
- **Priority:** P2
- **Dependencies:** none
- **Expected outcome:** Settings editable from the UI later without `.env` editing.
- **Acceptance criteria:** Tests for defaults, override precedence, invalid path rejection.

### 2.5 Job manager and SQLite schema
- **Description:** Implement `jobs.py` (one worker thread, cancel `Event`, status transitions) and `db.py` (`jobs`, `items`, `events`). Mark jobs left in `downloading` as `interrupted` on startup.
- **Priority:** P1
- **Dependencies:** 1.1, 2.1
- **Expected outcome:** Downloads run independently of any UI; state survives restarts.
- **Acceptance criteria:** Tests: a job moves queued → crawling → downloading → done; cancel stops within one chunk; restart converts a running job to `interrupted`; two jobs for the same course never run concurrently.

---

## Phase 3 — Authentication improvements

### 3.1 Typed session validation
- **Description:** `check_session()` performs one authenticated request and returns `valid | expired | network_error`. Do not map network failures to "expired" (M-2). Call it on connect, before each job, and on demand.
- **Priority:** P1
- **Dependencies:** 2.2
- **Expected outcome:** Correct messages; expired sessions caught before a job starts, including courses with a cached crawl.
- **Acceptance criteria:** Mocked 401/403 → `expired`; connection error/timeout → `network_error`; 200 → `valid`; a job on a cached course still triggers the check.

### 3.2 Remove dependence on the engine's hardcoded canary course
- **Description:** Make our own pre-flight check authoritative so the engine's `learning-how-to-learn` probe cannot cause false "expired" errors; translate its exception into the typed error if it still fires.
- **Priority:** P2
- **Dependencies:** 3.1
- **Expected outcome:** No false expiry from an unrelated course.
- **Acceptance criteria:** Test: engine raises `CookiesExpiredException` → mapped to `AuthExpired` with the app's own guidance text (no mention of `cookies.txt`).

### 3.3 Minimize and protect cookies
- **Description:** Keep cookies only in process memory. Try the minimum cookie set the engine needs (start with `CAUTH` only; keep the full set only if live testing shows it is required). Write the temp cookie file under `data/tmp/` with 0600, delete in `finally`, and sweep leftovers at startup.
- **Priority:** P1
- **Dependencies:** 2.1
- **Expected outcome:** Smaller secret footprint (M-3).
- **Acceptance criteria:** Tests: file removed after success, error and cancel; stale file removed at startup; no cookie values in logs or API responses.

### 3.4 Live per-browser verification matrix (manual)
- **Description:** On Windows, verify Firefox, Edge and Brave: logged in, logged out, browser open vs closed, with and without Administrator rights. Record results in the README troubleshooting section. Verify manual CAUTH fallback.
- **Priority:** P1
- **Dependencies:** none (can run any time)
- **Expected outcome:** Honest support statement per browser (L-7).
- **Acceptance criteria:** A table of browser × condition × result is committed; each failing cell has user-facing guidance in the app.

### 3.5 Session lifecycle UI states
- **Description:** Header shows `Connected via <browser>`, `Session expired – reconnect`, or `Not connected`; a failed job due to expiry offers a one-click reconnect then retry.
- **Priority:** P2
- **Dependencies:** 3.1
- **Expected outcome:** Users recover from expiry without confusion.
- **Acceptance criteria:** Simulated expiry mid-queue marks the remaining jobs `paused: auth` rather than failing them, and they run after reconnect.

---

## Phase 4 — Download reliability

### 4.1 Robust fetch loop
- **Description:** In `downloader.py`: `(connect, read)` timeouts, stream to `.part`, atomic rename, skip complete existing files, `Range` resume when the server returns 206, size check against `Content-Length`, exponential backoff with jitter, respect `Retry-After` on 429, no retries on 401/403/404 except one re-gather attempt.
- **Priority:** P0 once Phase 1 is done (it extends 1.1)
- **Dependencies:** 1.1
- **Expected outcome:** Interrupted downloads resume; no truncated files left under final names (M-4).
- **Acceptance criteria:** Local-server tests: disconnect mid-body then resume completes with correct bytes; 429 with `Retry-After` waits and succeeds; slow server triggers timeout and retry; existing complete file is skipped; `.part` never survives as a final file.

### 4.2 Safe file naming
- **Description:** Sanitize every path segment (separators, control characters, trailing dots/spaces, Windows reserved names), cap segment and total path length for Windows, resolve and contain under the download root, and de-duplicate collisions deterministically.
- **Priority:** P1
- **Dependencies:** 1.6
- **Expected outcome:** Valid, predictable names on Windows.
- **Acceptance criteria:** Parametrized tests including `CON`, trailing dots, 300-character titles, unicode, `..`, and two items with the same title.

### 4.3 Cancel and cleanup
- **Description:** Cancel flips the job's event; the downloader exits between chunks, leaves `.part` for later resume, and marks items `cancelled`.
- **Priority:** P1
- **Dependencies:** 2.5, 4.1
- **Expected outcome:** Real cancel (replaces the non-existent button).
- **Acceptance criteria:** Test: cancel during a slow download returns within one chunk interval; no child threads remain; job status `cancelled`.

### 4.4 Cache refresh and safer cache format
- **Description:** Add "Refresh course structure" that discards `crawl.pkl`/`gather.json` for a course; store structure as JSON instead of `pickle.load`ing from the download folder; re-gather when a cached task is older than a configurable age or a download returns 403/expired. Evaluate `dl_coursera` 1.1.0 for built-in cache invalidation before writing our own.
- **Priority:** P2
- **Dependencies:** 2.1
- **Expected outcome:** Updated courses and expired URLs recover automatically (M-5).
- **Acceptance criteria:** Test: changing the fake course (new lecture) then refreshing yields the new item; no `pickle.load` call remains in our code path.

### 4.5 Tighten content-type classification
- **Description:** Replace extension heuristics with an explicit, documented mapping (video, subtitle, pdf, reading/HTML, notebook, other); decide and document whether generated reading HTML and `bundle.zip` resources honor the user's selection (M-7).
- **Priority:** P2
- **Dependencies:** 1.1
- **Expected outcome:** Categories mean what the UI says.
- **Acceptance criteria:** Table-driven tests for each extension and for an extensionless file; selecting only "video" writes no reading HTML (or the behavior is explicitly documented and shown in the UI).

### 4.6 Rate limiting and politeness
- **Description:** Default one worker; small delay between requests; handle 429/403 bursts by backing off the whole job, not just one file.
- **Priority:** P2
- **Dependencies:** 4.1
- **Expected outcome:** Lower chance of account throttling.
- **Acceptance criteria:** Fake server that returns 429 for N requests: job completes, total request rate stays under the configured limit.

---

## Phase 5 — Frontend migration (recommended: Option B)

### 5.1 FastAPI shell and security middleware
- **Description:** `main.py` with `create_app()`; bind `127.0.0.1`; Host-header validation; per-launch token; no CORS; CSP and `nosniff` headers; `run.py` launcher that opens the browser with the token.
- **Priority:** P1
- **Dependencies:** Phases 1–2
- **Expected outcome:** A secure local API skeleton.
- **Acceptance criteria:** Tests: wrong Host → 400; missing token → 401; cross-origin POST → 403; response carries the security headers; server refuses non-loopback host without an explicit flag.

### 5.2 Auth and course routes
- **Description:** `GET /api/auth/status`, `POST /api/auth/connect`, `POST /api/auth/disconnect`, `GET /api/courses`, with typed error bodies.
- **Priority:** P1
- **Dependencies:** 5.1, 3.1
- **Expected outcome:** Connect and list courses over HTTP.
- **Acceptance criteria:** API tests with mocked services cover success and each error code; no response contains a cookie value.

### 5.3 Download and settings routes plus SSE
- **Description:** `POST /api/downloads`, `GET /api/downloads`, `POST /api/downloads/{id}/cancel`, `POST /api/downloads/{id}/retry`, `GET/PUT /api/settings`, `GET /api/events` (snapshot then deltas).
- **Priority:** P1
- **Dependencies:** 2.5, 5.1
- **Expected outcome:** Full control and live progress from a browser.
- **Acceptance criteria:** A test client receives `job.updated` events during a fake download; reconnecting receives a fresh snapshot; invalid slug returns `invalid_slug`.

### 5.4 Static UI (HTML, modern CSS, vanilla JS)
- **Description:** Single page with header (auth status), Add Course panel, Downloads list (active, queued, history), Log panel, minimal Settings. No framework, no build step, no CDN; responsive layout; keyboard-accessible controls.
- **Priority:** P1
- **Dependencies:** 5.2, 5.3
- **Expected outcome:** Usable download manager covering the initial-release scope.
- **Acceptance criteria:** Manual checklist: connect, list, start, watch progress, cancel, retry, view history and log, change folder; works at 360 px and 1280 px widths; Lighthouse accessibility score reviewed; no external network requests (checked in browser dev tools).

### 5.5 Remove Streamlit
- **Description:** Delete `app.py`, `streamlit` from requirements, Streamlit lines from README and `.gitignore`.
- **Priority:** P1
- **Dependencies:** 5.4 acceptance passed
- **Expected outcome:** Single UI, smaller install.
- **Acceptance criteria:** `pip freeze` has no `streamlit`; README run instructions use `run.py`/`scripts/run.ps1`.

---

## Phase 6 — User experience improvements (after the MVP)

### 6.1 Course library view
- **Description:** Scan download folders using per-course `manifest.json`; show downloaded courses, size, last updated, missing-file detection.
- **Priority:** P2
- **Dependencies:** 5.4, 4.2
- **Expected outcome:** See what you already have.
- **Acceptance criteria:** Library lists a locally created sample tree; deleting a file shows it as missing.

### 6.2 Update an existing course
- **Description:** Refresh structure, then download only new or missing items.
- **Priority:** P2
- **Dependencies:** 4.4, 6.1
- **Expected outcome:** Incremental updates without re-downloading.
- **Acceptance criteria:** Fake course gains one item; update downloads exactly one file.

### 6.3 Open folder and disk-space info
- **Description:** Backend-initiated "Open folder" (slug only, never a path); show free space and warn before a job if space is clearly insufficient.
- **Priority:** P3
- **Dependencies:** 5.4
- **Expected outcome:** Convenience features.
- **Acceptance criteria:** Open-folder route rejects unknown slugs; low-space warning appears in a test with a stubbed disk-usage function.

### 6.4 Resolution and subtitle-language options
- **Description:** Add only if the engine can honor them (verify against `dl_coursera`); otherwise leave out.
- **Priority:** P3
- **Dependencies:** 4.5
- **Expected outcome:** Optional choices that actually work.
- **Acceptance criteria:** Engine capability documented; options hidden when unsupported.

Deferred: dashboard summary tiles, queue reordering, scheduling, notifications, pause (cancel plus resume covers it), quizzes/notebooks unless the engine supports them.

---

## Phase 7 — Testing and documentation

### 7.1 Test infrastructure
- **Description:** Add `pytest-cov`, `responses` (or `pytest-httpx`), `ruff`; create `tests/fake_coursera.py` (local HTTP server serving memberships, course tree, assets) and `tests/fixtures/sample_course/`; add `pytest` markers `unit` and `integration`.
- **Priority:** P1
- **Dependencies:** none (start with Phase 1)
- **Expected outcome:** End-to-end tests with no live Coursera access.
- **Acceptance criteria:** One integration test runs crawl → gather → download → verify files against the fake server in under 30 seconds.

### 7.2 Regression suite
- **Description:** Tests for C-1, H-1, M-6, M-2 (network error ≠ expired), cookie-file cleanup, cancel, resume, log redaction.
- **Priority:** P0 for C-1/H-1/M-6 (write with the fixes), P1 for the rest
- **Dependencies:** respective fixes
- **Expected outcome:** Fixed bugs stay fixed.
- **Acceptance criteria:** Each listed finding has at least one failing-before, passing-after test; coverage of `coursera_app/` at least 80% excluding `web/`.

### 7.3 Continuous integration
- **Description:** GitHub Actions on Windows and Linux, Python 3.11 and 3.12: install, `ruff`, `pytest`, `pip-audit`.
- **Priority:** P1
- **Dependencies:** 7.1
- **Expected outcome:** Every push checked automatically.
- **Acceptance criteria:** Green pipeline on a clean clone; a deliberately failing test turns it red.

### 7.4 Documentation
- **Description:** Rewrite README (install, run, authenticate, troubleshoot, security notes, tested browsers), add `docs/ARCHITECTURE.md` (condensed from the recommendation), keep `MASTER_PLAN.md` in sync, add `LICENSE`, add a terms-of-use note.
- **Priority:** P1
- **Dependencies:** 5.5
- **Expected outcome:** A new user can install and run without help.
- **Acceptance criteria:** A person who has not seen the project follows the README on a clean Windows machine and downloads a course they are enrolled in.

---

## Phase 8 — Final release preparation

### 8.1 Supported-platform policy and live verification
- **Description:** Define supported Python versions (3.11 and 3.12 recommended) and Windows versions; complete the live checklist for one real enrolled course (auth, list, download, repeat download with a different selection, cancel, resume after killing the process).
- **Priority:** P1
- **Dependencies:** Phases 1–5
- **Expected outcome:** Verified, honest support statement.
- **Acceptance criteria:** Signed-off checklist stored in `docs/`.

### 8.2 Launcher and portable build
- **Description:** `run.ps1`/`run.bat` that creates the virtualenv on first run, starts the server and opens the browser. Evaluate a PyInstaller or embeddable-Python zip only if the launcher proves too technical for the target user.
- **Priority:** P2
- **Dependencies:** 8.1
- **Expected outcome:** Double-click start.
- **Acceptance criteria:** Fresh Windows user profile: double-click launches the app with no manual commands.

### 8.3 Versioning and release process
- **Description:** Single source of version (`__version__`), changelog, tagged GitHub release with the zip; document upgrade and troubleshooting, including how to pin or upgrade `dl-coursera`.
- **Priority:** P2
- **Dependencies:** 8.1
- **Expected outcome:** Repeatable releases.
- **Acceptance criteria:** Tag produces a release artifact; upgrade notes tested from the previous tag.

### 8.4 Engine contract tests
- **Description:** A small test that imports `dl_coursera_run` and asserts the functions and signatures the adapter relies on, run in CI against the pinned version and against the latest, so an engine update that breaks the adapter is caught early (L-4).
- **Priority:** P2
- **Dependencies:** 7.3
- **Expected outcome:** Early warning on upstream changes.
- **Acceptance criteria:** CI job fails when a required function or signature is missing.

---

## Suggested first sprint

1.1, 1.2, 1.3, 1.4, 1.5, 1.6 with their regression tests (7.2 subset). That is the smallest set that turns the current app from "looks finished, fails silently" into "works, and says so when it doesn't".

## Stop point

Per the brief, no roadmap item has been started. Implementation begins only after you review and approve these findings.
