# BUILD_PLAN — scaffold and build order for jenozu/coursera-dl

Status: plan only. Nothing has been written to the repo yet. Based on the three approved audit documents.

## 1. Approach

- Work on a branch `rebuild/fastapi`; `main` keeps the working Streamlit app until the new UI passes its checklist (roadmap 5.5).
- The scaffold is **stubs plus guidance**, not finished code: every module has a docstring, typed function signatures that raise `NotImplementedError`, and a matching test file with `xfail` or `skip` markers. Claude Code then fills them in one milestone at a time.
- A `CLAUDE.md` at the repo root tells Claude Code the rules, the build order and the definition of done, so any session can resume from the repo alone.
- Existing good code (`browser_auth.py`, `config.py`, cookie and filter helpers in `download_engine.py`, current tests) is kept and moved, not rewritten.
- Audit reports go into `docs/audit/` so the finding IDs (C-1, H-2 …) stay referenceable from code comments and commits.

## 2. Target folder structure

```
coursera-dl/
├── CLAUDE.md                    # rules + build order for Claude Code (new)
├── README.md                    # rewritten in milestone M0
├── MASTER_PLAN.md               # kept, synced with ROADMAP
├── LICENSE                      # new (you choose: MIT suggested)
├── pyproject.toml               # project metadata, ruff + pytest config (new)
├── requirements.txt             # runtime: fastapi, uvicorn, requests, rookiepy, dl-coursera==1.0.1
├── requirements-dev.txt         # pytest, pytest-cov, responses, ruff, pip-audit, httpx
├── run.py                       # launcher: start server on 127.0.0.1, open browser with token
├── app.py                       # OLD Streamlit app, kept until M7, then deleted
├── scripts/
│   ├── setup.ps1                # create venv, install deps (updated)
│   ├── run.ps1                  # activate venv, run run.py
│   ├── dev.ps1                  # run tests + ruff in one command
│   └── check_engine.py          # prints dl_coursera version + required signatures
├── coursera_app/
│   ├── __init__.py              # __version__
│   ├── main.py                  # create_app(): routes, middleware, static mount
│   ├── settings.py              # JSON settings + env override
│   ├── errors.py                # typed errors + HTTP mapping
│   ├── security.py              # slug validation, safe paths, host/token checks
│   ├── logging_setup.py         # rotating log + secret redaction filter
│   ├── browser_auth.py          # existing, unchanged
│   ├── engine.py                # dl_coursera adapter: crawl + gather + filter (from download_engine.py)
│   ├── downloader.py            # own fetch loop: .part, Range, retries, cancel
│   ├── jobs.py                  # job manager: worker thread, cancel events
│   ├── db.py                    # sqlite3 access
│   ├── schema.sql               # jobs, items, events
│   ├── services/
│   │   ├── auth_service.py      # session store, check_session(), memberships request
│   │   ├── course_service.py    # list courses, refresh structure
│   │   └── download_service.py  # create job, retry, summarize
│   ├── api/
│   │   ├── auth.py  courses.py  downloads.py  settings.py  events.py  logs.py
│   └── web/
│       ├── index.html  app.css  app.js     # no framework, no build step, no CDN
├── tests/
│   ├── conftest.py              # tmp dirs, fake server fixture, fake rookiepy
│   ├── fake_coursera.py         # local HTTP server: memberships, course tree, assets
│   ├── fixtures/sample_course/  # hand-made course JSON + tiny files (no real content)
│   ├── unit/                    # security, settings, errors, engine filter, cookies, db
│   ├── integration/             # crawl → gather → download against the fake server
│   └── api/                     # FastAPI TestClient tests
├── docs/
│   ├── audit/                   # AUDIT_REPORT.md, ARCHITECTURE_RECOMMENDATION.md, IMPROVEMENT_ROADMAP.md
│   ├── ARCHITECTURE.md          # short version, written in M7
│   └── LIVE_CHECKLIST.md        # manual Windows verification steps (browser x condition table)
├── data/                        # git-ignored: app.db, settings.json, logs/, tmp/
└── .github/workflows/ci.yml     # ruff, pytest, pip-audit on Windows and Linux, Python 3.11 and 3.12
```

Not carried over: `coursera_app/auth.py` (legacy), `coursera-dl` and its five helper dependencies, `streamlit`, `python-dotenv` (replaced by JSON settings plus an env override; keep the dotenv package only if you want `.env` files to keep working).

## 3. Scaffold contents (what I would create first)

| File | Scaffold content |
|---|---|
| `CLAUDE.md` | Project purpose, hard rules (local-only, no secrets in logs/DB, no live-Coursera tests, no unrequested dependencies), commands, milestone list with checkboxes, definition of done per task |
| `pyproject.toml` | Package metadata, `ruff` rules, `pytest` config with markers `unit`, `integration`, `api`, coverage settings |
| `errors.py` | Complete: `AppError` base plus `AuthExpired`, `CourseNotFound`, `NetworkError`, `DiskError`, `RateLimited`, `InvalidSlug`, each with `code`, `status`, `hint` (small, no logic to debate) |
| `security.py`, `settings.py`, `logging_setup.py`, `engine.py`, `downloader.py`, `jobs.py`, `db.py`, services, api | Docstring, signatures, `NotImplementedError`, link to the roadmap task ID |
| `schema.sql` | The three tables from the architecture document |
| `tests/` | One test file per module with the acceptance criteria from the roadmap written as named, skipped tests (`test_rejects_traversal_slug`, `test_second_run_downloads_new_selection` …) so Claude Code turns each from skip to pass |
| `fake_coursera.py` | Skeleton server with the endpoints listed, returning data from `fixtures/sample_course/` |
| `scripts/*.ps1`, `run.py` | Working versions; `run.py` fails with a clear message until `main.py` exists |
| `ci.yml` | Working pipeline (tests skipped initially, so it is green from the first push) |
| `docs/audit/*`, `docs/LIVE_CHECKLIST.md` | Your three reports copied in; checklist table pre-filled with empty cells |

## 4. Build order (milestones, each ends with passing tests and a commit)

| Milestone | Roadmap tasks | Result |
|---|---|---|
| **M0 Repo prep** | 1.5, 7.1 (infra only), 1.4 | Branch, scaffold, docs, CI, fake server skeleton, README fixed |
| **M1 Critical fixes (on current app)** | 1.1, 1.2, 1.3, 1.6, 7.2 subset | C-1, H-1, H-2, M-6 fixed and regression-tested; Streamlit app safe to keep using |
| **M2 Backend core** | 2.1, 2.2, 2.3, 2.4, 3.3, 4.2 | Legacy package gone; typed errors; logging with redaction; safe paths and cookie file |
| **M3 Downloads engine** | 4.1, 4.3, 2.5, 4.4, 4.5 | Robust fetch loop, job manager, SQLite, cancel, cache refresh, classification |
| **M4 Auth hardening** | 3.1, 3.2, 3.5 | Typed session check, no false expiry, pre-flight check before each job |
| **M5 API** | 5.1, 5.2, 5.3 | FastAPI app with security middleware, REST routes, SSE |
| **M6 Web UI** | 5.4 | Single-page UI covering: auth status, add course, active/queue, history, log, minimal settings |
| **M7 Cutover and docs** | 5.5, 7.3, 7.4, 8.4 | Streamlit and old files removed; docs final; CI green |
| **M8 Live verification and release** | 3.4, 8.1–8.3 | Windows checklist signed off; launcher; tagged release |

Only M8 and roadmap item 3.4 need you at a computer with a real Coursera account.

## 5. How a Claude Code session should run

1. Read `CLAUDE.md`, find the first unchecked milestone.
2. Create a task list from that milestone's roadmap items.
3. For each item: un-skip its tests, implement, run `scripts/dev.ps1`, commit with message `M2: <what> (roadmap 2.2)`.
4. Update the checkbox in `CLAUDE.md` and `MASTER_PLAN.md`.
5. Stop at milestone end, summarize, wait for review.

## 6. Decisions I need from you before scaffolding

1. **Where to put it:** push the scaffold to a new branch `rebuild/fastapi` on `jenozu/coursera-dl` (recommended), or commit to `main`.
2. **License:** MIT, or another? (The engine is MIT; the legacy LGPL package is being removed.)
3. **Config style:** keep `.env` support through `python-dotenv`, or JSON settings only (recommended).
4. **Python versions:** target 3.11 and 3.12 (recommended), or 3.11 only.
5. **Windows-only or cross-platform scripts:** PowerShell scripts only (recommended since you run Windows), or add `.sh` equivalents.

Defaults if you just say "go": new branch, MIT, JSON settings only, Python 3.11 and 3.12, PowerShell only.
