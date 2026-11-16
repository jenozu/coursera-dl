# Project rules (owned by this project)

<!-- Seeded once by master-harness and never replaced by an upgrade. Rules here override `rules.md` and the
     harness skills and agents wherever they conflict. Put owner rules here: things agents must always or never
     do in this project (e.g. "take a database restore point before any migration"). Keep it short.
     Merge behaviour (auto / safe-only / owner, and whether merging deploys) lives in `.claude/harness.json`,
     not here: the merge gate script enforces that file. -->

- (none yet)
- Hard rules from CLAUDE.md apply to every agent: bind `127.0.0.1` only; no CDN, external script, telemetry or paid service; never store, log or return cookies, CAUTH values or signed-URL query strings; never test against live Coursera or download protected content; never bypass Coursera authentication.
- Add a dependency only if a roadmap task calls for it, and say why in the commit message.
- Reuse working code (`browser_auth.py`, cookie/filter helpers) instead of rewriting it. No front-end framework, no build step, no Celery/Redis.
- The Streamlit app (`app.py`, `auth.py`, `download_engine.py`) must keep working until phase 7, then it is deleted.
- Scripts are Windows PowerShell (`scripts/*.ps1`); keep them idempotent and print what each step does.
- Commit messages: `M<phase>: <what> (roadmap <id>)`. At the end of each phase tick the milestone in CLAUDE.md and MASTER_PLAN.md.
