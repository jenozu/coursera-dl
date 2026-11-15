# CLAUDE.md — instructions for Claude Code

Local-first manager for downloading Coursera course material the user's own account is enrolled in.
Target: FastAPI backend + plain HTML/CSS/JS front end, SQLite for jobs, files on disk.

Read first: `docs/audit/AUDIT_REPORT.md` (finding IDs like C-1, H-2), `docs/audit/ARCHITECTURE_RECOMMENDATION.md`, `docs/audit/IMPROVEMENT_ROADMAP.md` (task IDs like 1.1). Roadmap tasks carry the acceptance criteria.

## Hard rules
1. Local only. Bind to `127.0.0.1`. No CDNs, no external scripts, no telemetry, no paid services.
2. Never store, log or return cookies, CAUTH values or signed-URL query strings. Redact in logs.
3. Never test against live Coursera and never download protected content. Tests use `tests/fake_coursera.py` and `tests/fixtures/sample_course/`.
4. Do not bypass Coursera authentication or access restrictions.
5. Add a dependency only if a roadmap task calls for it; explain why in the commit message.
6. Reuse working code (`browser_auth.py`, cookie/filter helpers) instead of rewriting.
7. Simple and small. No frameworks on the front end, no build step, no Celery/Redis.
8. Streamlit app (`app.py`, `auth.py`, `download_engine.py`) stays working until milestone M7, then is deleted.

## Commands (Windows PowerShell)
- Setup: `.\scripts\setup.ps1`
- Run old app: `streamlit run app.py --server.address 127.0.0.1`
- Run new app (after M5): `.\scripts\run.ps1`
- Check everything: `.\scripts\dev.ps1` (ruff + pytest)
- Engine contract check: `python scripts/check_engine.py`

## Workflow per session
1. Find the first unchecked milestone below.
2. Create a task list from its roadmap items.
3. For each item: un-skip the matching tests in `tests/`, implement, run `dev.ps1`, commit as `M2: <what> (roadmap 2.2)`.
4. Tick the checkbox here and in `MASTER_PLAN.md`.
5. Stop at the end of the milestone, summarize, wait for review.

Stub modules raise `NotImplementedError` and name their roadmap task in the docstring. Skipped tests are named after acceptance criteria.

## Milestones
- [x] **M0 Repo prep** — roadmap 1.5, 1.4, 7.1: README fixed, CI green, fake server working
- [ ] **M1 Critical fixes on current app** — 1.1, 1.2, 1.3, 1.6 + regression tests (fixes C-1, H-1, H-2, M-6)
- [ ] **M2 Backend core** — 2.1, 2.2, 2.3, 2.4, 3.3, 4.2 (legacy `coursera-dl` removed)
- [ ] **M3 Download engine** — 4.1, 4.3, 2.5, 4.4, 4.5 (fetch loop, jobs, SQLite, cancel)
- [ ] **M4 Auth hardening** — 3.1, 3.2, 3.5
- [ ] **M5 API** — 5.1, 5.2, 5.3 (FastAPI, security middleware, SSE)
- [ ] **M6 Web UI** — 5.4
- [ ] **M7 Cutover and docs** — 5.5, 7.3, 7.4, 8.4 (delete Streamlit, final docs)
- [ ] **M8 Live verification and release** — 3.4, 8.1–8.3 (needs the user on Windows with a real account)

## Definition of done (every task)
- Acceptance criteria from the roadmap are met and covered by tests.
- `ruff` clean, `pytest` green, no new warnings.
- No secrets in code, logs, DB or test output.
- Docs touched if behavior changed.
