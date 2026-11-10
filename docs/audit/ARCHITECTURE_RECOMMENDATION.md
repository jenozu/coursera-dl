# ARCHITECTURE_RECOMMENDATION — Coursera Downloader

Companion to `AUDIT_REPORT.md` (finding IDs such as C-1 and H-2 refer to it). Planning only; no code was changed.

## 1. Assessment of the current architecture

```
Browser ── Streamlit (app.py, 200 lines, owns UI + state + long-running work)
              ├─ browser_auth.py   rookiepy → cookies          (good, reusable)
              ├─ auth.py           legacy coursera-dl session   (replace)
              ├─ config.py         .env settings                (good)
              └─ download_engine.py adapter → dl_coursera_run   (reusable, needs a new download step)
```

Strengths: small, one-directional dependencies, the engine is already behind an adapter, secrets are never persisted, config is non-secret.

Weaknesses:
- The UI process *is* the job runner. Streamlit reruns the script on every interaction, so background work, cancel, queue and restart recovery are structurally awkward (H-5).
- Two Coursera access layers (legacy session for listing, `dl_coursera` for crawling) and two cookie shapes.
- No job model: nothing records what was requested, what succeeded, what failed.
- Network exposure and telemetry defaults come from the framework (H-2, L-1).
- The engine's `download()` carries hidden state in cache files (C-1) and reports nothing back (H-1).

## 2. The eight questions

1. **Can the existing download logic be reused?** Mostly. Keep the engine's `crawl` and `gather_dl_tasks` (these turn a slug into a list of `{url, filename}` tasks plus locally generated reading files). Replace its `download()` with a small downloader of our own, because we need per-file results, progress, cancel, resume and no hidden failed-list state. Reuse unchanged: `browser_auth.py`, `config.py`, cookie-file writer, filter function (after tightening, M-7).
2. **Which modules need refactoring?**
   - `download_engine.py`: split into `engine.py` (crawl+gather → task list) and `downloader.py` (our fetch loop).
   - `auth.py`: drop the legacy import, implement session check and course listing with `requests`.
   - `app.py`: delete after migration; logic moves to API routes.
   - New: `jobs.py` (job manager), `db.py`, `errors.py`, `security.py`.
3. **Can Streamlit be removed entirely?** Yes. Only `app.py` imports it, and nothing else depends on it.
4. **Would FastAPI be sufficient?** Yes. It gives typed request/response models, SSE support (via `StreamingResponse`), static file serving for the HTML, and a clear place for security middleware. No other web framework is needed.
5. **Would background tasks need a separate worker or queue?** No. FastAPI's built-in `BackgroundTasks` is not enough on its own (no cancellation, no status), but a tiny in-process job manager is: one `ThreadPoolExecutor(max_workers=1)` (or 2 for later), a `threading.Event` per job for cancel, and job state in SQLite. The engine and `requests` are blocking, so run them in threads, not on the event loop. Celery/Redis/RQ would be over-engineering for a single-user local tool.
6. **WebSockets or Server-Sent Events?** SSE. Progress is one-way (server → page); `EventSource` is built into browsers, reconnects automatically, works over plain HTTP, and needs no extra library. Send a full snapshot on connect, then deltas. If you want the very simplest first version, polling `GET /api/jobs` once a second also works and can be swapped for SSE later without changing the data model. WebSockets only make sense if the page must send frequent messages back, which it doesn't.
7. **Is SQLite necessary?** Needed once you want queue, history and restart recovery, which the plan's Phases 5–6 require. Python's standard `sqlite3` module adds no dependency. Flat JSON files would also work for a handful of jobs, but then you hand-write atomic writes and locking. Recommendation: SQLite for jobs, items and events; JSON for settings; the filesystem (plus a small `manifest.json` per course) as the source of truth for downloaded files, so the library can be rebuilt if the database is lost.
8. **Limitations of this architecture:**
   - The biggest risk is not architectural: Coursera's endpoints are unofficial and change, so crawl/gather will break periodically regardless of front end. Keep the engine behind one interface and pin its version.
   - Reading browser cookies depends on `rookiepy` and OS/browser behavior (locked databases, admin requirements, browser encryption changes). Keep manual CAUTH as a fallback.
   - A web page cannot open a native folder picker or "show in Explorer"; the backend must do it (`os.startfile` on Windows), and only on request from localhost.
   - Non-technical Windows users need a launcher (double-click `.bat`/exe that starts the server and opens the browser).
   - Localhost services are still reachable by other local web pages (DNS rebinding, cross-site requests); see section 7.
   - Per-host browser connection limits (about 6 on HTTP/1.1) apply to SSE; use one stream per page.
   - Windows path-length limits (260 characters) hit long course/lesson titles; the downloader must shorten names.
   - Signed asset URLs may expire while queued; re-gather before download if a task is older than a threshold (expiry behavior unverified).

## 3. Options compared

| | A. Keep Streamlit, improve | B. HTML/CSS/JS + FastAPI (recommended) | C. Desktop app (Qt, Tauri, Electron) |
|---|---|---|---|
| What changes | Fix bugs, add `threading` + `st.session_state` queue, `st.fragment` polling | Replace `app.py` with API + static pages; reuse Python logic | New UI toolkit, packaging, possibly a second language |
| Advantages | Least change now; keeps current UI; fast to patch C-1/H-1 | Real background jobs, cancel, queue; persistent state independent of page; tiny frontend, no build step; easy to test the API with `pytest`; can later be wrapped (pywebview) or served to nothing but localhost; lighter than Streamlit | Native feel, tray icon, folder pickers, single installer |
| Disadvantages | Rerun model fights long jobs; background threads and session state are fragile; no persistence across tabs/restarts; heavy dependency; binds all interfaces by default (fixable by config); hard to build a dashboard/queue UI | You write the HTML/JS (about 600–900 lines for the MVP) and the security middleware; browser limits on file/folder integration | Largest build; Electron/Tauri add Node/Rust toolchains (against "minimal dependencies"); installers, code signing, auto-update; highest maintenance |
| Complexity | Low now, rising steeply with each feature in Phases 5–7 | Medium, flat afterward | High |
| Maintenance cost | Medium-high (fighting the framework) | Low-medium (stdlib-style code, few dependencies) | High (UI toolkit, packaging, platform quirks) |
| Fit to goals ("polished lightweight download manager", local-first, minimal deps) | Poor beyond a single-page tool | Good | Over-scoped |

**Verdict: B.** Do the critical fixes inside the current app first (they are small and should not wait), then migrate. Option C can be revisited only if you later want a tray icon or installer, and B can be wrapped in `pywebview` at that point without a rewrite.

## 4. Recommended architecture

```
Browser (vanilla JS, SSE)
   │  http://127.0.0.1:<port>   (Host-header check, per-launch token)
   ▼
FastAPI app (uvicorn, one process)
   ├─ api/        REST routes + SSE stream
   ├─ services/   auth, courses, downloads (pure Python, no web imports)
   ├─ jobs.py     in-process job manager: 1 worker thread, cancel events
   ├─ engine.py   adapter → dl_coursera crawl + gather
   ├─ downloader.py  requests-based fetch: .part files, Range resume, retries
   ├─ db.py       sqlite3 (jobs, items, events)
   └─ settings.py JSON settings (download dir, concurrency, preferences)
   ▼
Filesystem: <download_dir>/<course-slug>/…  + manifest.json per course
```

Key rules:
- `services/` knows nothing about FastAPI, so it can be tested directly and the front end can be swapped later.
- Cookies live only in process memory (a `SessionStore` object) and in a short-lived 0600 temp file while crawling; never in SQLite, JSON settings or logs.
- One engine interface: `crawl(slug) -> CourseTree`, `gather(tree, selection) -> list[Task]`. Only `engine.py` imports `dl_coursera_run`.

## 5. Proposed project structure

```
coursera-dl/
├── README.md  MASTER_PLAN.md  LICENSE  pyproject.toml
├── requirements.txt  requirements-dev.txt
├── run.py                       # starts uvicorn on 127.0.0.1, opens the browser
├── scripts/setup.ps1  scripts/run.ps1
├── coursera_app/
│   ├── __init__.py
│   ├── main.py                  # create_app(), middleware, static mount
│   ├── settings.py              # JSON settings (replaces .env use)
│   ├── errors.py                # typed errors → HTTP codes
│   ├── security.py              # host check, token, slug + path validation
│   ├── api/                     # auth.py courses.py downloads.py events.py settings.py
│   ├── services/                # auth_service.py course_service.py download_service.py
│   ├── engine.py                # dl_coursera adapter (crawl + gather)
│   ├── downloader.py            # own fetch loop
│   ├── jobs.py                  # job manager
│   ├── db.py  schema.sql
│   ├── browser_auth.py          # existing, kept
│   └── web/                     # index.html, app.css, app.js (no build step)
├── tests/
│   ├── unit/  integration/  fixtures/sample_course/   # locally created sample data
│   └── fake_coursera.py         # local fake server
└── data/                        # git-ignored: app.db, settings.json, logs/
```

## 6. Frontend/backend communication

Proposed REST surface (all JSON, all under `/api`, all require the launch token):

| Method + path | Purpose |
|---|---|
| `GET /auth/status` | Connected? source browser? last check time |
| `POST /auth/connect` `{browser}` or `{cauth}` | Read cookies / accept manual value; validate with one memberships call |
| `POST /auth/disconnect` | Clear in-memory session |
| `GET /courses` | Enrolled courses (cached for the session; `?refresh=1`) |
| `POST /downloads` `{slug, types[]}` | Validate slug, create job, enqueue |
| `GET /downloads` | Queue, active, history (`?status=`) |
| `POST /downloads/{id}/cancel` / `/retry` | Cancel running or queued job; retry failed items |
| `GET /events` | SSE stream: `job.updated`, `item.updated`, `auth.changed`, `log` |
| `GET/PUT /settings` | Download folder, concurrency, selection defaults |
| `GET /logs?level=` | Recent activity and errors (tail of the log file) |
| `POST /library/open` `{slug}` | Ask the backend to open the folder in Explorer (localhost only) |

Errors return `{error: {code, message, hint}}` with stable codes (`auth_expired`, `course_not_found`, `network`, `disk_full`, `rate_limited`, `invalid_slug`) so the UI can show friendly, actionable messages.

## 7. Data storage strategy

SQLite (`data/app.db`, `sqlite3` with WAL mode):

```
jobs(id, slug, title, types_json, status, created_at, started_at, finished_at, error_code, error_msg)
items(id, job_id, url_hash, rel_path, kind, status, bytes_done, bytes_total, attempts, error_code)
events(id, ts, level, job_id, message)            -- pruned to the last N thousand
```

Status values: `queued, crawling, downloading, done, done_with_errors, failed, cancelled`.
- Item rows replace the engine's hidden `download.dl_tasks_failed.json`, fixing C-1 at the root: selection and outcome live in one place that we control.
- `settings.json` holds download folder, concurrency (default 1), preferred types.
- On startup, jobs left in `downloading` become `interrupted` and can be resumed (the downloader uses `.part` files, so resume is real).
- Never stored: cookies, CAUTH, passwords, signed URLs in plain log lines.

## 8. Download processing strategy

1. **Crawl** (per job, in the worker thread): write the 0600 cookie file → `engine.crawl` → delete the file in `finally`. Treat cached crawl data as optional; offer "Refresh course structure". Prefer JSON over pickle for cached structure (M-5).
2. **Gather and filter**: build tasks with a tightened classifier (explicit extension sets, documented categories, M-7); sanitize and length-limit every path segment; verify the final path is inside the download root.
3. **Fetch** (own `downloader.py`):
   - `requests.Session`, `(connect, read)` timeouts, streaming to `<name>.part`, `os.replace` on completion;
   - skip if the final file exists with a non-zero size (and matches `Content-Length` when known);
   - resume with `Range` if `.part` exists and the server answers 206; otherwise restart;
   - retry with exponential backoff and jitter on network errors, 5xx and 429 (respect `Retry-After`), no retry on 401/403/404 except one re-auth/re-gather attempt;
   - check a `threading.Event` between chunks for cancellation.
4. **Report**: every item ends as `done`, `skipped`, or `failed(code)`; the job summary is derived from items (fixes H-1).
5. **Concurrency**: one job at a time and one file at a time by default (polite to Coursera, simple to reason about); expose a small concurrency setting later.

## 9. Security considerations

Binding and request security (FastAPI replaces Streamlit's open listener):
- Bind to `127.0.0.1` only. Refuse to start with another host unless an explicit unsafe flag is passed.
- Validate the `Host` header (`127.0.0.1:<port>` or `localhost:<port>`) to defeat DNS rebinding.
- Generate a random token at launch; the launcher opens the browser at `/?token=…`, the page keeps it in memory and sends it as `Authorization` on every API call (SSE via query token or fetch-based stream). This blocks other local web pages and other local users.
- No CORS headers at all (same origin only); reject cross-origin `Origin` on state-changing requests; `Content-Type: application/json` required on POST.
- Add `Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff`; no third-party scripts, fonts or CDNs (also keeps it local-first).
- Never return cookies or CAUTH in any response; redact `CAUTH` and signed-URL query strings in logs.

Filesystem safety:
- Validate slugs with `^[a-z0-9][a-z0-9-]{0,127}$` before any path or URL use (M-6); resolve every output path and require it to be under the download root; sanitize titles (strip separators, control characters, trailing dots/spaces, Windows reserved names; cap length).
- The "open folder" route accepts only a known course slug, never a path.
- Temp cookie file: 0600 on POSIX, in the app's own `data/tmp/` on Windows; remove at job end and sweep leftovers at startup.

Supply chain: pin `dl-coursera`; run `pip-audit` in CI; keep dependencies to `fastapi`, `uvicorn`, `requests`, `rookiepy`, `dl-coursera` (plus `python-dotenv` if kept). Remove `streamlit` and the legacy `coursera-dl` stack.

## 10. UX scope (initial release vs deferred)

| Proposed screen | Initial release | Notes |
|---|---|---|
| Authentication status | **Yes** | Connect from browser, manual fallback, clear expired-session state; always visible in the header |
| Add Course | **Yes** | Pick from enrolled list; paste URL/slug fallback (validated); content-type checkboxes |
| Active downloads | **Yes** | Per-job progress, per-file list, Cancel |
| Download queue | **Yes (merged with Active)** | One list with statuses queued/running; reorder deferred |
| Download history | **Yes (simple)** | Finished/failed jobs from SQLite, Retry failed items, Open folder |
| Error and activity log | **Yes (simple)** | Last N events with level filter; this doubles as diagnostics |
| Dashboard | Defer | The merged active/history page is the dashboard; add summary tiles later |
| Course library | Defer | Needs the manifest scanner and "update course" logic; do after history works |
| Download settings | **Minimal** | Download folder, content-type defaults; resolution/subtitle language only after the engine proves it can honor them |

Avoid in v1: accounts, themes, drag-and-drop reordering, scheduling, pause (cancel + resume covers it), notifications, multi-user features.

## 11. Migration order (summary)

1. Fix critical bugs inside the existing app (C-1, H-1, H-2, H-3, docs).
2. Extract `services/` and the downloader with tests, still callable from Streamlit.
3. Remove the legacy package.
4. Add FastAPI routes over the services; build the static UI; run both UIs briefly if useful.
5. Delete `app.py` and Streamlit once the new UI covers the MVP list above.

This order means each step ships something working and the Python logic is tested before the UI changes.
