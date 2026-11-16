# Instructions for AI coding assistants (Claude Code, Cursor, Codex, Copilot...)

Coursera Downloader: a local-first manager (FastAPI + plain HTML/JS) for downloading Coursera course material the user's own account is enrolled in; one user, Windows, 127.0.0.1 only.

This repo is built task by task from a written plan. Follow this loop exactly; it exists to stop the project
drifting away from the plan.

## Where the plan lives
- `.taskmaster/docs/prd.md`: goal, non-goals, success criteria, stack, decision log. `tasks.py show` prints the
  goal and non-goals; open the PRD when a task needs more.
- `.taskmaster/tasks/tasks.json`: phases, tasks, subtasks, status, dependencies, test strategy, work log. Source of truth.
- `.taskmaster/docs/parking-lot.md`: ideas that are NOT in the plan.
- `.taskmaster/docs/manual-checks.md`: checks waiting for a human or an agent with a running app.
- `.taskmaster/docs/human-checklist.md`: steps only the human can do (queued, not blocking). Tick them when done.
- `TASKS.md`: generated from tasks.json. Never edit by hand.

Helper (Python stdlib only), from the repo root, in bash (on Windows: Git Bash, not PowerShell):
```
python .taskmaster/tasks.py status | phase [n] | next [--phase n] [--details] | show <id>
python .taskmaster/tasks.py set-status <id> in-progress|done|deferred|cancelled
python .taskmaster/tasks.py log <id> 'plan: ...'     # timestamped note (single quotes; or `- <<'EOF'` for any text)
python .taskmaster/tasks.py add --help               # add a task or subtask
python .taskmaster/tasks.py validate                 # after any manual edit of tasks.json
python .taskmaster/render_tasks_md.py                # refresh TASKS.md
```

## Work loop (one task at a time)
1. `tasks.py next --details` (task, goal and non-goals in one call). Complexity 7+ without subtasks: split it into 3-5 subtasks first.
2. Read the code the task touches. Log your plan: `tasks.py log <id> 'plan: files X, Y; approach ...'`.
3. `tasks.py set-status <id> in-progress`, build it, log what worked and what failed.
4. Run the task's testStrategy for real. Not done until it passes.
5. Drift check, `set-status <id> done`, `render_tasks_md.py`, commit with the id: `task 7.2: <title>`, push the branch.

## Drift rules
- Only work on the task `next` returned. New ideas → dated line in `parking-lot.md`.
- Changing what's being built → PRD decision log first, then tasks, then code.
- Never reword a `done` task; add a corrective subtask. Cancel tasks, never delete them.

## Project
- Stack: Python 3.11/3.12, FastAPI + uvicorn, requests, rookiepy, dl-coursera==1.0.1 (crawl+gather only), stdlib sqlite3 + threading (coursera_app/); plain HTML/CSS/vanilla JS in coursera_app/web/; legacy Streamlit app (app.py, auth.py, download_engine.py) stays until M7
- Install: `powershell -File scripts/setup.ps1`
- Test: `.venv/Scripts/python.exe -m pytest -q`
- Lint: `.venv/Scripts/python.exe -m ruff check .`
- Build: `n/a`
- Dev servers: defined in `.claude/dev-servers.json`; run with `python .claude/scripts/devserver.py start all`.

## Facts that are easy to get wrong
- Hard rules live in the project instructions: bind 127.0.0.1 only, no CDN/telemetry, never log or return cookies, CAUTH or signed-URL query strings.
- Never test against live Coursera and never download protected content: tests use tests/fake_coursera.py and tests/fixtures/sample_course/.
- Do not bypass Coursera authentication or access restrictions.
- Add a dependency only when a roadmap task calls for it, and say why in the commit message.
- No front-end framework or build step; no Celery/Redis/ORM.
- Stub modules raise NotImplementedError and name their roadmap task in the docstring; skipped tests are named after acceptance criteria. Each task un-skips its tests first.
- Finding IDs (C-1, H-2) are in docs/audit/AUDIT_REPORT.md; task IDs (1.1, 2.2) with acceptance criteria are in docs/audit/IMPROVEMENT_ROADMAP.md. Grep them, do not read in full.
- Windows PowerShell scripts: scripts/setup.ps1, dev.ps1 (ruff + pytest), run.ps1. Engine contract check: python scripts/check_engine.py.
- Streamlit app (app.py, auth.py, download_engine.py) stays working until phase 7, then is deleted.
- Commit message style: `M2: <what> (roadmap 2.2)`. Tick milestones in CLAUDE.md and MASTER_PLAN.md at the end of each phase.
