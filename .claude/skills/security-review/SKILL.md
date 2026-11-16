---
name: security-review
description: Focused security pass over the whole app before shipping or after auth, permission or data-handling changes. Produces findings as fix tasks. Use when the human asks for a security review, before the first deploy, or when a phase touched auth.
disable-model-invocation: true
---

# Security review

Dispatch the **reviewer** agent per area below (one area per dispatch, to keep each context small). For each,
it reads the relevant code and reports findings with file:line, a concrete exploit or failure, and the fix.

1. **Secrets:** `git grep -n -I -E "(api[_-]?key|secret|password|token)\s*[:=]" -- ':!*.lock'`; committed `.env`
   files (`git ls-files | grep -i env`); secrets in logs or error messages.
2. **Secrets in flight:** cookies, CAUTH values and signed-URL query strings never appear in logs, SQLite rows, API
   responses, exceptions or test output; the 0600 temp cookie file is removed after every job and swept at startup.
3. **Local server:** bound to `127.0.0.1` only; Host allowlist, per-launch token and Origin checks reject foreign
   requests; no CORS; CSP and `nosniff` set; no external requests from the web UI.
4. **Input:** slug validation, path containment under the download dir, sanitized Windows-safe filenames,
   SQL only with bound parameters, no HTML injection in the UI (textContent, not innerHTML).
5. **Dependencies:** `pip-audit` if available; note high/critical only.

Each finding → `python .taskmaster/tasks.py add --title "Security: <issue>" --review --complexity <n>
--details "<file:line, exploit, fix>" --test "<how to prove it's fixed>"`. Report counts by severity in 5 lines.
