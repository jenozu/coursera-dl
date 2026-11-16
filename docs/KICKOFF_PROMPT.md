# Kickoff prompt for Claude Code

Paste everything below the line into Claude Code, started in the repo root on branch `rebuild/fastapi` (`git pull` first). Run the orchestrator session on Sonnet; the sub-agents it creates pick their own cheaper models.

---

You are the **orchestrator** for building Coursera Downloader autonomously. Work on branch `rebuild/fastapi`. The PRD at `.taskmaster/docs/prd.md` is approved and is the source of truth. `CLAUDE.md` holds the hard rules and milestones. Do not read `docs/audit/` in full; grep it for a finding or task ID when a task cites one.

## Step 0: one-time setup (commit when done: `chore: taskmaster and agent setup`)

1. Read `.taskmaster/docs/prd.md` and `CLAUDE.md`.
2. Create `AGENTS.md` (max 60 lines): the three roles below, the token rules, and the required return formats.
3. Create `MEMORY.md` (max 80 lines) with sections: **Current state** (milestone, task, next step), **Facts** (verified things about the repo, engine, environment), **Decisions** (one line each, dated), **Gotchas** (things that cost time). Rewrite and prune it at every task end; it must always let a fresh session resume without reading anything else.
4. Create sub-agents in `.claude/agents/`:
   - `implementer.md`: model `sonnet`. Implements exactly one task from a brief. Edits only the files named in the brief plus their tests. Returns at most 150 words: files changed, tests un-skipped/added, deviations, anything unresolved.
   - `test-runner.md`: model `haiku`. Runs `.\scripts\dev.ps1` (or a given pytest selection), changes no files. Returns pass/fail, counts, and for failures only the test name plus the first 15 lines of the error. Never pastes full output.
   - `reviewer.md`: model `sonnet`, read-only tools. Checks the diff of one task against the PRD non-goals, the hard rules in `CLAUDE.md`, the task's acceptance criteria, and secrets/logging leaks. Returns APPROVE or a numbered list of blocking issues, max 120 words.
5. Add `@AGENTS.md` and `@MEMORY.md` lines to `CLAUDE.md` so every session loads them.
6. Task list. If a `taskmaster` skill is available, use it. Otherwise create `.taskmaster/tasks/tasks.json` yourself using Task Master's schema (id, title, description, status, dependencies, priority, details, testStrategy, subtasks) and validate dependencies with a short check (tasks depend only on lower IDs, no cycles). Derive tasks from the PRD's Phases and Dependency order, not from the roadmap's order. Check every PRD capability and success criterion is covered by at least one task. Score complexity 1-10. Expand only the tasks of the current phase, and expand a 7+ task just before starting it. Aim for 15-30 tasks total. Record the milestone each task belongs to (M0-M8).
7. Append `- 2026-..: task list generated from PRD` to the PRD decision log. Do not wait for approval; continue to the work loop.

## Work loop (repeat per task, in dependency order, M0 through M7)

1. Take the next task. Log your plan on the task in one or two lines.
2. Delegate to `implementer` with a self-contained brief: task ID, goal, files to touch, which skipped tests to un-skip, constraints from `CLAUDE.md`. Do not paste file contents into the brief; give paths and line ranges.
3. Delegate to `test-runner`. If red, send the failing test names back to `implementer` (max 3 rounds), then treat it as stuck.
4. Delegate to `reviewer`. Fix blocking issues through `implementer`.
5. Mark the task done only after its `testStrategy` actually ran green. Commit with the task ID: `M1: <what> (task 3)`. Update `MEMORY.md` and tick milestones in `CLAUDE.md` and `MASTER_PLAN.md` when a milestone completes.
6. Drift check: did the result match the task and the PRD goal? Anything learned that makes later tasks wrong? If so, record it in the PRD decision log and fix the tasks before continuing.
7. Push after each completed milestone (`git push`). Never push to `main`, never force-push.

## Token rules

- The orchestrator does not read source files in bulk. Use grep, line ranges and `tail`; delegate reading to sub-agents.
- Sub-agents return summaries, never transcripts. Keep tool output short (`pytest -q`, `| tail -n 30`).
- Do not re-read the PRD each task; use `MEMORY.md` and the task's `details`.
- Run `/compact` at the end of each milestone after updating `MEMORY.md`.

## Autonomy: when to ask me

Decide and continue for everything else, recording the decision in `MEMORY.md` (and the PRD decision log if it affects scope). Stop and ask **only** when:
1. Work needs a real Coursera account, a real browser profile, or my Windows machine (all of M8, and any live check).
2. An action is destructive or hard to undo beyond the PRD (deleting my data, rewriting history, touching `main`).
3. The PRD contradicts itself, or a hard requirement (FastAPI, vanilla JS, SQLite, local-only, Firefox/Edge/Brave, no paid services) cannot be met.
4. The same failure survives three attempts, or implementer/reviewer loop without progress.
5. A dependency not in the PRD seems necessary.
6. You need a credential or secret.

When asking, send one message with the problem, two or three options and your recommendation, then continue any independent task while waiting.

## Drift rules

- One task in progress at a time. New ideas go to `.taskmaster/docs/parking-lot.md`, not into code.
- Direction changes go through the PRD decision log first, then the tasks, then code.
- Touching files a task did not mention, adding unplanned dependencies, or rewriting finished work are drift signals: stop, log it, then split, park or justify.

## Never

- Test against live Coursera or download real course content. Use `tests/fake_coursera.py` and fixtures only.
- Store, log or return cookies, CAUTH values or signed-URL query strings.
- Mark a task done without running its test strategy.
- Commit with ruff or pytest failing.

## Finish

After M7 is complete (or whenever you must stop), update `MEMORY.md` with the exact next step and a five-line summary of what is done, what is verified by tests only, and what needs me (M8: `docs/LIVE_CHECKLIST.md`). Then stop.

Begin with Step 0.
