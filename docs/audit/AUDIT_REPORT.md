# AUDIT_REPORT — Coursera Downloader

Repository: `jenozu/coursera-dl` (branch `main`, 41 commits, last commit `f35f398`)
Audit date: 2026-11-09
Scope: audit and planning only. No application code was modified.

## 1. Executive summary

The project is a small (~520 lines of Python plus 144 lines of tests) Streamlit front end over three pieces: a browser-cookie reader (`rookiepy`), the legacy `coursera-dl 0.11.5` package (used for one API call), and the maintained `dl_coursera 1.0.1` package (used for crawling and downloading). The refactor from a single-file prototype is clean and the test suite passes (10/10), and the app starts and renders under Python 3.11 (checked with Streamlit's `AppTest`).

**It is not yet reliable.** The code that exists is thin glue, and the glue has defects that make the core flow untrustworthy:

1. A second download of the same course silently downloads nothing, and the UI still says "Finished" (verified, see C-1).
2. Download failures are never reported; the UI always reports success (H-1).
3. The documented install steps produce an app that crashes on import (H-3).
4. Streamlit listens on all network interfaces by default, and the "Connect from Browser" button reads the host machine's browser cookies, so anyone on the same network can use the owner's Coursera session (H-2).
5. README claims progress display, log viewer, retry/cancel controls and logout-style credential management that do not exist in `app.py` (H-4).

Most of the repository's value is in `browser_auth.py`, `config.py` and the `download_engine.py` adapter, all of which can be reused. `app.py` (200 lines) and `auth.py` (51 lines, depends on the legacy package) are the parts to replace.

**What I could not verify:** nothing was run against live Coursera, Windows, or real Firefox/Edge/Brave profiles (no credentials, and the brief forbids touching protected content). Everything marked "unverified" below needs a live check by you on Windows. The repository's own README says the same: "awaiting live Windows verification".

## 2. Current project status

`MASTER_PLAN.md` says Phase 1 is nearly done (one unchecked item: "Verify the app still imports/starts"), Phase 2 is done, and Phases 3–8 are untouched except one Phase 4 item (engine swap to `dl_coursera`). My assessment against that plan:

| Plan phase | Plan status | Audit finding |
|---|---|---|
| 1 Foundation | 9/10 | Done. The unchecked item is now verified: the app imports and starts on Python 3.11 when the legacy package is installed. README structure section is stale. |
| 2 Browser auth | all checked | Implemented, unit-tested with mocks only. Live reading from the three browsers is unverified. Expired-session handling is weak (M-2). |
| 3 Course library | 0/7 | Only "retrieve enrolled courses" exists (via legacy package), and it is not ticked. |
| 4 Engine | 1/17 | Crawl, gather and download run through `dl_coursera`. Several unticked items are partly provided by the engine (folder structure, subtitles, PDFs) but nothing is verified. |
| 5–8 | 0 | Not started. |

## 3. Features that work (verified)

- App imports and renders the logged-out screen with no exceptions (Python 3.11, legacy package installed).
- `config.py`: reads `COURSERA_DOWNLOAD_DIR` with a safe default.
- `browser_auth.py` logic: browser allow-list, CAUTH lookup, helpful error messages (mocked `rookiepy`).
- `download_engine.py` adapter logic: Netscape cookie file creation (mode 0600 on Linux, deleted in `finally`), cache-directory pre-creation, `crawl()` signature detection (3-arg and 4-arg), extension-based task filtering.
- Test suite: 10 passed. Ran in a clean Python 3.11 environment.
- No tracked secrets: no `.env`, `.pkl`, or cookie files in `git ls-files`; the history contains no credentials.
- The adapter does not call `dl_coursera_run.main()`, so the engine's PyPI version-check request is never made. No engine telemetry is reached.

## 4. Features that are broken

| ID | Feature | Evidence |
|---|---|---|
| C-1 | Downloading a course a second time with a different content selection | Verified by probe, see below |
| H-1 | Failure reporting | Code inspection: `dl_coursera_run.download()` returns `None`; failures are written to a JSON file the app never reads |
| H-3 | Documented installation | Fresh environment from `requirements.txt` fails with `ModuleNotFoundError: No module named 'coursera'` on `import coursera_app.auth` |

## 5. Features that are incomplete or only claimed

README "Current Features" versus `app.py`:

| README claim | Reality |
|---|---|
| Download progress display | A single `st.status` box with two text lines. Real progress (tqdm) goes to the console only. |
| Download log viewer | Not present. |
| Retry/cancel controls | Not present. Engine retries each file up to 3 times internally (`ttl=3`); the user cannot cancel. |
| Local credential update/logout | Only a "Disconnect" button that clears session memory. No stored credentials exist. |
| Video, subtitle, PDF, assignment, supplementary filtering | Present, but see M-7 for how loosely these categories map to files. |
| Reads "only the CAUTH cookie" | Out of date. Since commit `4207d8d` every `coursera.org` cookie is kept in session state and written to the temp cookie file. |

Planned and not implemented: course search, course detail view, URL/slug entry, resolution and subtitle-language selection, quizzes and notebooks, resume, queue, persistent history, SQLite, settings, disk-space info, distribution.

## 6. Critical bugs and findings by severity

### Critical

**C-1. Re-downloading the same course silently does nothing, or downloads the wrong files.**
`dl_coursera_run.download()` loads `<out>/<slug>/.cache/download.dl_tasks_failed.json` if it exists and *replaces* the task list you passed with its contents. After any run, the engine writes that file (an empty list `[]` on success). Verified with a fake downloader:

- Run 1 (videos) completes and writes `[]`. Run 2 (PDFs, same course) calls `download()`, loads `[]`, sees zero tasks and returns. **No downloader is invoked.** The app then shows "Download finished".
- If run 1 had failures, run 2 downloads only the previously failed files and ignores the new selection.

Impact: the "pick content types, click Download" flow works once per course. Anyone who downloads videos first and PDFs later, or retries after fixing a problem, gets silent no-ops. Fix location: do not use the engine's `download()`; own the download step (Roadmap 1.1).

### High

**H-1. Failures are reported as success.** `download_course()` returns `total_tasks` and `download_tasks` (counts of tasks attempted, not completed). The UI prints "Finished" regardless of how many files failed. Failed tasks are recorded only in the engine's JSON file and `main.log`, neither of which the UI reads.

**H-2. The app is reachable from the local network and can use the host's browser session.** Verified: `streamlit run app.py` starts Uvicorn on `0.0.0.0` and prints a "Network URL". Streamlit has no authentication. "Connect from Browser" runs `rookiepy` on the *server* machine, so any device on the same Wi-Fi can open the page, click it, and get the owner's Coursera session (course list, downloads into the owner's disk). `.streamlit/` is in `.gitignore`, so a fix via `.streamlit/config.toml` cannot even be committed. Streamlit also prints a usage-statistics prompt by default (`browser.gatherUsageStats`).

**H-3. Documented setup yields a crashing app.** `requirements.txt` has a comment saying the legacy package is retained, but the package is not listed. It must be installed separately with `--no-deps` (README step 3 and `setup.ps1` do this, a plain `pip install -r requirements.txt` does not). Without it, `app.py` fails on import. The five transitive legacy dependencies (`six`, `keyring`, `pyasn1`, `configargparse`, `attrs`) are listed in `requirements.txt` only to serve it.

**H-4. README overstates the product.** See section 5. This matters because users will rely on a Cancel button that does not exist.

**H-5. Downloads run inside Streamlit's script thread.** The whole crawl-and-download call is synchronous in the page script. Streamlit reruns the script on any widget interaction and stops the previous run, so clicking another control, or closing the tab, can abort a download mid-file. There is no cancel and no way to leave and come back. Two browser tabs can start two downloads into the same course directory and cache with no locking.

### Medium

**M-1. Unmaintained legacy dependency for one call.** `coursera-dl 0.11.5` (LGPL; Python 2/3.4–3.6 classifiers; pins `attrs==18.1.0`, the reason for the `--no-deps` workaround) supplies `get_session()` and `list_courses()`. On Python 3.11 it emits `SyntaxWarning: "is" with a literal` at import. It imports `distutils`, which was removed from the standard library in 3.12; it only works there if `setuptools` supplies a shim. `list_courses()` is a single GET to the memberships endpoint (`https://api.coursera.org/api/memberships.v1?includes=courseId,courses.v1&q=me&showHidden=true&filter=current,preEnrolled`) and reading `reply['linked']['courses.v1'][*]['slug']`. That is about ten lines of `requests` code.

**M-2. Weak authentication-error handling.**
- `list_courses()` converts *every* exception into "Your login may have expired", including network outages and timeouts.
- Sessions are validated once, at connect time. Nothing re-checks before a download starts.
- `dl_coursera_run.crawl()` returns the cached `crawl.pkl` *before* it checks the cookies, so an expired session is not detected for any course that was crawled before.
- Its freshness check requests a hardcoded course (`learning-how-to-learn`) and treats an "unauthorized" reply as expired. If that course or response shape changes, every user gets a false "expired" error. When the check does fire, the message says "The cookies.txt expired", which is meaningless to this app's users.
- The adapter wraps all engine errors in `DownloadEngineError(str(exc))`, discarding exception type, so the UI cannot distinguish expired session, course not found, network failure and disk error.

**M-3. Full cookie jar kept in memory and written to disk.** All `coursera.org` cookies (not only CAUTH) are held in `st.session_state` and written to a temp Netscape file for each download. The file is created with mode 0600 on Linux and removed in `finally`; if the process is killed mid-download it remains in the temp directory. Windows file permissions for the temp file are unverified. Whether the engine needs more than `CAUTH` is untested; reducing to the minimum set is worth trying.

**M-4. The built-in downloader is not robust.** (`dl_coursera.Downloader.DownloaderBuiltin`): `requests.get(url, stream=True)` with no timeout; writes straight to the final filename (an interrupted file is indistinguishable from a complete one); no HTTP Range resume; no skip-if-exists; no size or hash check; one worker thread; retries limited to 3 attempts with no backoff or 429 handling. Cross-checked: resume flags exist only for the optional aria2 downloader, which this app does not use.

**M-5. Crawl cache never refreshes.** `crawl.pkl` and `gather.json` are reused forever (v1.0.1). New lectures, changed assets, or expired signed asset URLs in `gather.json` (whether Coursera signs these URLs with expiry is unverified) are not picked up. `dl_coursera 1.1.0` adds cache invalidation keyed on options but also renames cache files and changes `crawl()`, which is why the adapter sniffs the signature. `crawl.pkl` is loaded with `pickle.load`, which is unsafe on a shared or synced download folder (Low in a single-user local setting).

**M-6. Course slug is not validated (latent path traversal).** Verified: `download_course(course_slug="../../escaped", ...)` is accepted and creates `<out>/../../escaped/.cache`. Today the slug comes from the dropdown, so exposure is low. It becomes a real vulnerability the moment Phase 3 adds free-text URL/slug entry or the API accepts a slug in a request body. (Inside the engine, asset names that contain `..` cannot climb above the course tree because the tree asserts at its root; only the first path segment, the slug, is unprotected.)

**M-7. Content-type filter semantics are loose.**
- "Videos" matches only `.mp4`; any other video container falls into "Supplementary".
- "Assignments / HTML" matches any `.html`/`.htm`.
- "Supplementary" is everything else, including extensionless files and `.ipynb`.
- Reading pages, supplement HTML and the 1.5 MB `bundle.zip` of CSS/JS are created during the gather stage regardless of selection, so choosing only "Videos" still writes reading HTML. The adapter's own docstring notes this.
- Quizzes, notebooks and graded assignments are not distinguished; whether engine 1.0.1 downloads them at all is unverified.

### Low

- **L-1.** Streamlit usage-statistics collection is on by default (conflicts with "local-first, no external services"). Disable via `browser.gatherUsageStats = false`.
- **L-2.** Documentation drift: README project-structure and test sections list only `auth.py`/`config.py`/`test_config.py`; README says "Phase 1" though Phase 2 is complete; `MASTER_PLAN.md` line 100 contains a literal `\n` inside the text.
- **L-3.** No `LICENSE` file, no CI, no linter or type checking, no lockfile. Dependencies use ranges (`>=`) except the engine.
- **L-4.** The adapter imports `dl_coursera_run`, which is the engine's command-line script module, not a documented API. It is pinned to `==1.0.1`, and the signature-sniffing code exists because the 1.1.0 API differs. Treat as an internal dependency: pin, wrap, and cover with contract tests.
- **L-5.** Application code has no `logging` usage at all. Errors are shown in the UI as raw `str(exc)`; nothing is written to a log for later diagnosis.
- **L-6.** The result field `download_tasks` means "tasks selected", not "tasks downloaded"; the UI text ("processed N") reads as completed work.
- **L-7.** Edge/Brave cookie reading may require running as Administrator (the code already warns). Whether current Chromium-based browser cookie-encryption changes break `rookiepy` for Edge or Brave on a given Windows version is unverified; add a live check per browser.

## 7. Security concerns (summary)

| Area | Finding | Severity |
|---|---|---|
| Local API exposure | Streamlit binds `0.0.0.0`, no auth; server-side cookie read reachable by LAN clients (H-2) | High |
| Cookie handling | Full jar in memory and a temp file; remains if process killed (M-3) | Medium |
| Path safety | Slug traversal accepted (M-6) | Medium (latent) |
| Deserialization | `pickle.load` of cache from download folder (M-5) | Low |
| Credentials at rest | Nothing persisted by the app; `.gitignore` covers `.env`, cookies, sessions, downloads | Good |
| Logs | App writes no logs; engine's `main.log` logs task dicts (URLs, filenames), may include signed URLs. Not reviewed live. | Low |
| Dependencies | `pip-audit` on the resolved runtime environment: no known vulnerabilities in project dependencies. It flagged only `pip` and `setuptools` in my scratch environment (tooling, not shipped) | None found |
| CORS/request security | Not applicable to Streamlit; must be designed in for FastAPI (see ARCHITECTURE_RECOMMENDATION.md) | n/a |
| Input validation | Slug unvalidated; download dir unrestricted (acceptable for a local, single-user setting) | see M-6 |

The brief asked not to bypass Coursera access controls. Nothing in the current code does; it uses the user's own session cookie for courses the account can open.

## 8. Dependency review

| Package | Used for | Finding | Recommendation |
|---|---|---|---|
| `streamlit` | UI | Heavy (large dependency tree), binds all interfaces, sends usage stats by default | Remove when migrating (only `app.py` uses it) |
| `python-dotenv` | `.env` | Fine, tiny | Keep, or replace with JSON settings file |
| `requests` | HTTP | Fine, also required by the engine | Keep; add timeouts everywhere |
| `rookiepy` | Browser cookies | Required for the feature; Rust-built wheels; maintenance status not verified | Keep; add a live per-browser check; keep manual fallback |
| `dl-coursera==1.0.1` | Crawl/gather/download | Maintained, MIT, reasonable. Adapter uses a non-public module and its `download()` has C-1 | Keep crawl+gather; replace `download()` with own code; evaluate 1.1.0 (cache invalidation) |
| `coursera-dl 0.11.5` (not in requirements) | `get_session`, `list_courses` | Unmaintained, `distutils`, SyntaxWarnings, LGPL, forced `--no-deps` workaround | **Remove**; replace with a ~10-line memberships request |
| `beautifulsoup4`, `six`, `urllib3`, `pyasn1`, `keyring`, `configargparse`, `attrs` | Legacy package's dependencies only | Redundant once legacy is removed (`beautifulsoup4` is also required by `dl_coursera`, which declares it itself) | Remove from `requirements.txt` after legacy removal |
| `pytest` | Tests | Fine | Keep; add `pytest-cov`, `responses` or `pytest-httpx`, `ruff` |

Why not replace things now: nothing above was changed; each removal is tied to a roadmap task with acceptance criteria.

## 9. Technical debt

- Streamlit page as an application: state, long-running work and UI in one script.
- Glue code depends on three upstream packages with two different Coursera access layers (legacy session + `dl_coursera` crawler). Two code paths means two failure modes and two cookie representations.
- Error handling by `except Exception` and string conversion throughout.
- No logging, no job model, no persistence, no concurrency control.
- Docs and plan drift.

## 10. Test coverage assessment

**Existing:** 3 test files, 10 tests, all passing; no coverage tool configured (assessment by inspection).

| Module | Covered | Gaps |
|---|---|---|
| `config.py` | Defaults, env override | Whitespace-only env value |
| `browser_auth.py` | All three browsers, unsupported browser, missing CAUTH (mocked) | Reader raising an exception (admin hint path); cookie list returned empty; Chrome name rejected |
| `download_engine.py` | 3-arg and 4-arg `crawl`, cache dir creation, one filter case | `_netscape_line` edge cases (expiry formats, non-Coursera domains), cookie temp-file cleanup on error, `_filter_download_tasks` for every category, empty selection, engine exception wrapping, slug validation |
| `auth.py` | **None** | Needs the legacy package; untested |
| `app.py` | **None** | Streamlit `AppTest` can exercise it |

**Missing unit tests:** cookie formatting; filter matrix; slug validation and path containment; error-type mapping; settings loading; job state machine (once built).

**Missing integration tests (no live Coursera needed):**
- Local fake Coursera: a small `http.server` or `responses`-based fixture serving memberships, course, lecture, supplement and asset JSON built by hand, so crawl → gather → download runs end to end.
- Downloader tests against a local HTTP server: success, 404, 429, 5xx then success, mid-stream disconnect, slow response (timeout), Range resume, existing complete file, truncated `.part` file.
- Auth: expired-session reply, network error, malformed JSON, empty course list.
- Fake `rookiepy` readers: locked database, no CAUTH, multiple CAUTH cookies across subdomains.

**Regression tests to add immediately:** C-1 (two successive runs with different selections both download), H-1 (a failing file yields a failed status and a non-"success" summary), M-6 (traversal slug rejected).

**Rule for testing:** use only locally created sample course data and fake servers. Do not download protected or unauthorized content in tests.

## 11. Final assessment

1. **Is the current application functional?** Partly. It starts and renders, and the first download of a course appears to be wired correctly, but I could not confirm live authentication or a real download, and the flow has silent-failure bugs. I would not rely on it yet.
2. **What currently works?** Startup, configuration, browser/cookie logic (mock-tested), adapter plumbing, engine invocation signatures, content filtering by extension, secret hygiene in git, passing test suite.
3. **What doesn't work?** Repeat downloads (C-1), failure reporting (H-1), documented install (H-3), cancel/progress/log/retry (claimed, absent), safe network binding (H-2), cache refresh (M-5).
4. **What needs fixing before adding features?** C-1, H-1, H-2, H-3 and the README correction, then slug validation. These are small, mostly a few dozen lines each.
5. **Keep Streamlit or migrate?** Migrate to FastAPI plus plain HTML/CSS/JS, after the critical fixes. Streamlit's rerun model is a poor fit for background downloads, cancellation and a persistent queue, which are the next three roadmap phases. See ARCHITECTURE_RECOMMENDATION.md.
6. **Can we reuse most of the backend?** Yes: `browser_auth.py`, `config.py`, the cookie/filter/slug parts of `download_engine.py`, and the engine's crawl and gather stages. Replace the engine's `download()` and the legacy `auth.py`.
7. **Simplest maintainable architecture?** One local Python process: FastAPI on `127.0.0.1`, a small in-process job manager (one worker thread), SQLite for jobs and history, the filesystem for files, a JSON settings file, and Server-Sent Events for progress.
8. **What to implement first?** (a) Own the download step with per-file results (fixes C-1 and H-1 together), (b) bind to localhost, (c) fix install and docs, (d) remove the legacy dependency, (e) regression tests for all of these. Then the FastAPI migration.
