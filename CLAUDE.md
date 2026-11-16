# Coursera Downloader: Claude Code instructions

@AGENTS.md

Local-first manager for downloading Coursera course material the user's own account is enrolled in.
Target: FastAPI backend + plain HTML/CSS/JS front end, SQLite for jobs, files on disk.
Read first: `docs/audit/AUDIT_REPORT.md` (finding IDs C-1, H-2), `docs/audit/ARCHITECTURE_RECOMMENDATION.md`,
`docs/audit/IMPROVEMENT_ROADMAP.md` (task IDs 1.1; acceptance criteria). Grep them, don't read in full.

## Hard rules
1. Local only. Bind to `127.0.0.1`. No CDNs, external scripts, telemetry or paid services.
2. Never store, log or return cookies, CAUTH values or signed-URL query strings. Redact in logs.
3. Never test against live Coursera or download protected content. Tests use `tests/fake_coursera.py` and `tests/fixtures/sample_course/`.
4. Do not bypass Coursera authentication or access restrictions.
5. Add a dependency only if a roadmap task calls for it; explain why in the commit message.
6. Reuse working code (`browser_auth.py`, cookie/filter helpers) instead of rewriting.
7. Simple and small. No front-end framework or build step, no Celery/Redis.
8. Streamlit app (`app.py`, `auth.py`, `download_engine.py`) stays working until phase 7, then is deleted.

## Commands (Windows PowerShell; agents use Git Bash)
Setup `.\scripts\setup.ps1` · old app `streamlit run app.py --server.address 127.0.0.1` · new app (after phase 5)
`.\scripts\run.ps1` · check everything `.\scripts\dev.ps1` (ruff + pytest) · engine contract `python scripts/check_engine.py`.
Commit style: `M2: <what> (roadmap 2.2)`. Tick the milestone here and in `MASTER_PLAN.md` when a phase ends.

## Roles: lead → phase-runner → builders
- **Builder, verifier or reviewer subagent:** follow your agent file; it overrides the AGENTS.md loop (you don't
  mark tasks done, commit or push). Ignore the rest of this section.
- **phase-runner subagent:** follow your agent file and the preloaded `next-task` procedure.
- **Main session = the lead** (run it on Opus). Run `/run-phase` and stay out of the details; act only on the
  phase-runner's final report.

| Agent | Model | Role |
|---|---|---|
| phase-runner | sonnet, medium | Runs a whole phase: routes, verifies, escalates, commits, reports once |
| builder-haiku / -sonnet / -opus | haiku / sonnet / opus | Complexity 1-3 / 4-6 / 7+, or after the tier below failed |
| verifier | haiku, read-only | Runs each task's testStrategy independently |
| reviewer | sonnet, read-only | Tasks flagged `review`, or diffs touching Risky paths |

Escalation: haiku → sonnet → opus per task; phase-runner → lead when opus fails, scope changes, something is
destructive, or the human is needed. Manual checks and human-only steps collect in
`.taskmaster/docs/manual-checks.md` and `human-checklist.md`. Phases end with a PR (`deliver`); `merge_gate.py`
merges per `.claude/harness.json`. Owner rules in `.claude/rules/project.md` override harness rules.
Commands are bash: on Windows, Git Bash.

## Phases (phase n = milestone Mn)
0 Prep (done) · 1 Critical fixes · 2 Backend core · 3 Download engine · 4 Auth hardening · 5 API · 6 Web UI ·
7 Cutover and docs · 8 Live verification (needs the user). See `tasks.py phase`.
- [x] M0 · [ ] M1 · [ ] M2 · [ ] M3 · [ ] M4 · [ ] M5 · [ ] M6 · [ ] M7 · [ ] M8

## Risky paths (reviewer required)
`coursera_app/security.py`, `main.py` (middleware) · `browser_auth.py` and anything touching cookies/CAUTH/signed URLs ·
`logging_setup.py` (redaction) · `downloader.py` (path containment, resume) · `schema.sql`, `db.py` ·
`app.py`, `auth.py`, `download_engine.py` (legacy, must keep working until M7).

## Skills
Core: `/run-phase [n|ids]` · `/status` · `/manual-checks run|results` · `/adapt` · `/plan-from-prd add-phase` ·
`deliver` · `dev-servers` · `next-task`. Project: `security-review`.

<!-- master-harness v2.2.1 -->
