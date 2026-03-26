---
name: redo
description: >
  Re-execute a previously completed task or check in the current session.
  Reruns tests, re-audits files, rechecks line counts, re-validates a phase,
  or repeats any action Claude already performed. Use when the user says
  "redo", "run again", "recheck", "do it again", "retry", "rerun",
  "one more time", or "repeat that".
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Redo — Re-Execute a Completed Task

The user wants to repeat something already done in this session.
Identify WHAT to redo and run it again from scratch.

**RULE: Execute the task fully — not a summary of previous results.**
**RULE: Use the latest file state, not cached results.**

---

## Phase 1 — Identify What to Redo

If $ARGUMENTS provided, match it:

| User says | Action |
|-----------|--------|
| `/redo tests` | Phase 2A — run test suite |
| `/redo lint` or `/redo ruff` | Phase 2B — run linter |
| `/redo check` | Phase 2C — run Django check |
| `/redo migrations` | Phase 2D — check migrations |
| `/redo line-check` or `/redo lines` | Phase 2E — check file sizes |
| `/redo phase N` | Phase 2F — re-execute plan phase N |
| `/redo [filename]` | Phase 2G — re-audit specific file |
| `/redo pre-commit` | Phase 2H — invoke /pre-commit skill |
| `/redo validate` | Phase 2I — invoke /validate skill |
| `/redo last` | Phase 2J — repeat last action |

If NO arguments, ask:
"Last action was: [description]. Redo this? Or specify with `/redo [task]`."

---

## Phase 2A — Tests

```bash
pytest --tb=short -q
```

If $ARGUMENTS specifies a path: `pytest [path] --tb=short`

Report: pass count, fail count, failures with file:line.

---

## Phase 2B — Lint

```bash
ruff check nai_planner/ tests/
```

---

## Phase 2C — Django Check

```bash
DJANGO_SETTINGS_MODULE=tests.settings python -m django check
```

---

## Phase 2D — Migrations

```bash
DJANGO_SETTINGS_MODULE=tests.settings python -m django makemigrations --check --dry-run
```

---

## Phase 2E — Line Check

For each `.py` file in project:

```bash
wc -l nai_planner/*.py nai_planner/models/*.py nai_planner/contrib/drf/*.py nai_planner/contrib/ninja/*.py nai_planner/management/commands/*.py tests/*.py
```

- Over 200 lines -> **FAIL**
- 180-200 lines -> **WARN**

---

## Phase 2F — Plan Phase N

Read most recent plan from `docs/plans/`. Find Phase N. Re-verify every task.

---

## Phase 2G — Specific File

Read the file fresh. Run:

1. `ruff check [file]`
2. Line count check (200 max for file)
3. Function length check (200 max)
4. If model file: `__str__`, `on_delete`, `max_length` checks
5. If view/viewset: user isolation, permissions
6. If Celery task: error handling, timeouts
7. Security: no hardcoded secrets, no raw SQL with f-strings

---

## Phase 2H-2J

- 2H: Execute full `/pre-commit` skill
- 2I: Execute full `/validate` skill
- 2J: Scan conversation for most recent action and re-verify

---

## Phase 3 — Output

```
## Redo — [what was redone]

**Action:** [description]
**Scope:** [files involved]
**Result:** PASS / FAIL / [N passed, M failed]

[Details]
```

If FAIL: list issues with file:line and suggested fix.
If PASS: "All clean. Move on."
