# Coursera Downloader memory (short-term project state)

<!-- Rules files without a `paths:` header load at the start of every Claude Code session, so nothing needs to
     import this. HTML comments like this one are stripped before loading and cost no context. -->

**Why this file exists:** so a new session knows where things stand without re-reading the PRD, task logs or
old chats. Open `.taskmaster/` only for the task you're working on.

**Who edits it:** the phase-runner, **once at the end of each run**, in its own commit. The lead also edits it
after resolving an escalation or when the human gives a fact worth keeping. Everyone else only reads it.
Never update it per task.

**Size rules (the point of the file):**
- Max ~80 lines. Each section has a cap; when it's full, delete the least useful line before adding one.
- Replace, don't append: "Now" is overwritten every time; outdated lines are deleted, not struck through.
- Only add to "Learned" what would save a future session 5+ minutes or prevent a repeat failure.
- Details belong in `tasks.py log <id>`; this file holds one-line pointers ("see 7.3 log").

---

## Now (overwrite each time, max 6 lines)
- Phase 1 complete 2026-11-16 on branch phase-1 (tasks 2-6); PR via deliver.
- Next: phase 2 (Backend core). Run `/run-phase 2`.
- In progress: none.
- Manual checks waiting: none.

## Facts (stable, max 15 lines)
- Dev machine: Windows 11, PowerShell + Git Bash, Python 3.12 venv at .venv.
- Local-only app: nothing is deployed; merging to main does not go live.
- Default branch: main. Work branch for the rebuild: rebuild/fastapi (M0 done there).
- Phase numbers equal milestone numbers (phase 3 = M3).
- Phase 8 needs the user on Windows with a real Coursera account.

## Decisions since the PRD (max 8 lines, newest first; full text in the PRD decision log)
- 2026-11-16: Built with master-harness v2.2.0: lead (Opus) → phase-runner (Sonnet) → builders
  haiku → sonnet → opus. Manual checks batched per phase.

## Learned / gotchas (max 15 lines, newest first)
- pytest default tmp (AppData\Temp\pytest-of-andel) is access-denied here; pytest.ini now sets --basetemp=.pytest_tmp.
- scripts/run.ps1 starts legacy Streamlit until M5; coursera_app/download_engine.py is ruff-excluded (legacy).
- app.py:209 doesn't catch InvalidSlug (parking-lot).

## Model routing record (update counts at each close-out)
| Tier | Done first try | Escalated up | Notes |
|---|---|---|---|
| haiku | 3 | 1 | |
| sonnet | 0 | 1 | |
| opus | 1 | 0 | |
<!-- If one tier escalates on 3 tasks in a row, the phase-runner escalates to the lead, who may raise that tier's
     starting complexity in .claude/skills/next-task/SKILL.md. If haiku passes everything, give it complexity 4 too. -->

## Open questions for the human (max 5; delete once answered)
- rookiepy on Windows with Edge/Brave may need Administrator or fail on new browser encryption: unverified until phase 8, manual CAUTH is the fallback.
- Do signed asset URLs expire while queued? Design re-gathers on 403.
- Which cookies beyond CAUTH does dl_coursera need? Try CAUTH only first.
- Can dl_coursera honor resolution / subtitle language? Out of v1 scope until proven.
