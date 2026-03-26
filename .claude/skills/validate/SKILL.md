---
name: validate
description: "Post-implementation validation gate for nai-planner. Verifies plan completeness, model integrity, API safety, migration state, and code standards. Run after finishing a task, before committing. Use when user says validate, verify, recheck, or final check."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Validate — Post-Implementation Verification

Final gate before code leaves this machine. Recheck the ENTIRE implementation.

**RULE: Do NOT fix anything. Report only.**
**RULE: Execute every phase in order.**
**RULE: Read every file — do not skim.**

---

## Phase 1 — Identify Scope

Read `CLAUDE.md` for project conventions.

!`git diff --name-only HEAD~3`
!`git diff --cached --name-only`
!`git status --short`
!`ls -t docs/plans/*.md 2>/dev/null | head -1`

Read the plan to understand what was implemented.
If $ARGUMENTS provided, scope to those items only.

---

## Phase 2 — Static Analysis

```bash
pytest --tb=short -q
ruff check nai_planner/ tests/
```

- Any test failure -> **FAIL**
- Any ruff error -> **FAIL**

---

## Phase 3 — Plan Completeness

Read the active plan file.

For each phase/task:
- `- [x]` done -> verify the work exists in code
  - "create file X" but file doesn't exist -> **FAIL**
  - "add model" but no model or migration -> **FAIL**
  - "add test" but no test file -> **FAIL**
- `- [ ]` incomplete -> **FAIL** — intentionally skipped?

If no plan: skip.

---

## Phase 4 — Model Integrity

For each changed model file in `nai_planner/models/`:

**FAIL:**
- ForeignKey without `on_delete`
- CharField without `max_length`
- Soft delete logic gaps

**WARN:**
- Missing `db_index=True` on lookup fields
- Missing `__str__` method
- N+1 query patterns

---

## Phase 5 — API Safety

For changed DRF files in `nai_planner/contrib/drf/`:

**FAIL:**
- Missing user isolation in get_queryset
- Missing permission_classes
- Serializer validation gaps

For changed Ninja files in `nai_planner/contrib/ninja/`:

**FAIL:**
- Missing authentication
- GenericFK resolution without error handling

---

## Phase 6 — Celery Tasks

For changed task files:

**FAIL:**
- Tasks without error handling
- External calls without timeout
- Per-item saves instead of bulk_update

**WARN:**
- Missing `max_retries`, `acks_late`, `time_limit`

---

## Phase 7 — Migration State

```bash
DJANGO_SETTINGS_MODULE=tests.settings python -m django makemigrations --check --dry-run 2>/dev/null
```

**FAIL:**
- Model changes without migration
- Migration conflicts

---

## Phase 8 — Code Standards

Per CLAUDE.md: max 200 lines per file and per function/class.

**FAIL:**
- File over 200 lines
- Function over 200 lines
- Hardcoded secrets, API keys, tokens
- `print()` statements
- `breakpoint()` or `pdb` imports
- Silent catch blocks

**WARN:**
- Approaching 200-line limit (180+)
- Magic strings/numbers

---

## Phase 9 — Security Scan

**FAIL:**
- Raw SQL with string formatting/f-strings
- `eval()`, `exec()`, `__import__()` on user input
- Shell commands with user input
- User-controlled input in `.filter(**kwargs)` via dict expansion
- Sensitive data in log output

---

## DO NOT FLAG

- Import ordering (ruff handles this)
- Trailing commas, whitespace, quote style
- Naming conventions (linter territory)
- Missing docstrings on private methods

---

## Phase 10 — Report

```
## Validation Report — [plan name or task]
Scope: [N files changed]

| # | Check | Result | Findings |
|---|-------|--------|----------|
| 1 | Static analysis | PASS/FAIL | N issues |
| 2 | Plan completeness | PASS/FAIL/SKIP | N issues |
| 3 | Model integrity | PASS/FAIL/SKIP | N issues |
| 4 | API safety | PASS/FAIL/SKIP | N issues |
| 5 | Celery tasks | PASS/FAIL/SKIP | N issues |
| 6 | Migrations | PASS/FAIL | N issues |
| 7 | Code standards | PASS/FAIL | N issues |
| 8 | Security | PASS/FAIL | N issues |
```

### Findings

For each FAIL: **File:Line** — description

### Write to `docs/issues.md`

```markdown
## Validation — YYYY-MM-DD — [plan name]
- [ ] description — file:line — priority: high/med/low
```

### Verdict

**VALIDATED** — all checks pass. Safe to commit.
or
**NOT VALIDATED** — N check(s) failed. Fix then run `/validate` again.
