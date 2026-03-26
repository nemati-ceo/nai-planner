---
name: full-app-audit
description: "Comprehensive audit of nai-planner Django package — models, API views, serializers, tasks, admin, signals, code quality, dependencies. Reports all findings to docs/issues.md, fixes nothing. Use when user says full audit, app audit, audit everything, health check, or find all bugs."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Full Package Audit — nai-planner

Find every bug, security gap, and convention violation. No compliments. Only problems.

**RULE: Do NOT fix anything. Report only.**
**RULE: Execute every phase in order.**
**RULE: Read actual file contents — do not guess.**

All findings go to `docs/issues.md`.

---

## Phase A — Gather Context

!`cat CLAUDE.md`
!`find nai_planner -name '*.py' | wc -l`
!`find nai_planner -name '*.py' -exec wc -l {} + | sort -rn | head -20`

If $ARGUMENTS provided, scope to those paths only.

---

## Phase B — Static Analysis

```bash
pytest --tb=short -q
ruff check nai_planner/ tests/
```

- **BLOCKER**: Test failure
- **HIGH**: ruff error

---

## Phase C — Model Audit

Scan `nai_planner/models/`:

- ForeignKey without explicit `on_delete` -> **HIGH**
- CharField without `max_length` -> **HIGH**
- Missing `__str__` method -> **LOW**
- Missing `db_index=True` on fields used in filters -> **MEDIUM**
- Missing `unique_together` or `UniqueConstraint` where appropriate -> **MEDIUM**
- Soft delete logic gaps -> **HIGH**

---

## Phase D — DRF API Audit

Scan `nai_planner/contrib/drf/`:

- **BLOCKER**: User isolation not enforced (missing user filter in get_queryset)
- **HIGH**: Missing permission_classes
- **HIGH**: Serializer validation gaps (linked_model, end_at)
- **MEDIUM**: Missing select_related on FK access
- **MEDIUM**: Inconsistent error responses

---

## Phase E — Ninja API Audit

Scan `nai_planner/contrib/ninja/`:

- **BLOCKER**: Authentication not enforced
- **HIGH**: GenericFK resolution without error handling
- **HIGH**: Schema inconsistency with DRF serializers
- **MEDIUM**: Missing error response schemas

---

## Phase F — Security Audit

Scan all `.py` files in `nai_planner/`:

**BLOCKER:**
- Hardcoded API keys, tokens, passwords, or secrets
- Raw SQL with string formatting/f-strings (SQL injection)
- `eval()`, `exec()`, `__import__()` on user input
- `mark_safe()` on user input (XSS)

**HIGH:**
- Sensitive data in log output
- Missing input validation
- Exceptions exposing internal paths or stack traces to callers

---

## Phase G — Celery Task Audit

Scan `nai_planner/tasks.py`:

**HIGH:**
- Tasks without error handling or retry logic
- Tasks making external calls without timeout
- Per-item saves that could use bulk_update

**MEDIUM:**
- Missing `max_retries`, `acks_late`, or `time_limit`
- FCM push without proper failure handling

---

## Phase H — Code Quality

Per CLAUDE.md: max 200 lines per file and per function/class.

- Files over 200 lines -> **HIGH** (identify split points)
- Functions/methods over 200 lines -> **HIGH**
- `print()` statements -> **MEDIUM** (use logger)
- `breakpoint()` or `pdb` imports -> **BLOCKER**
- Silent catch blocks (`except: pass`) -> **HIGH**
- Bare `except:` without logging -> **MEDIUM**

---

## Phase I — Admin & Signals

Scan `nai_planner/admin.py` and `nai_planner/signals.py`:

- Sensitive fields in `list_display` -> **HIGH**
- Signal handlers with undocumented side effects -> **MEDIUM**
- Admin list causing N+1 queries (FK in list_display) -> **MEDIUM**

---

## Phase J — Dependencies

Read `pyproject.toml`:
- Packages without version constraints -> **HIGH**
- Unused packages -> **MEDIUM**
- Missing packages that code imports -> **BLOCKER**

---

## Phase K — Report

Write to `docs/issues.md`:

```markdown
## Full Package Audit — YYYY-MM-DD

| # | File | Line | Phase | Issue | Severity |
|---|------|------|-------|-------|----------|
```

Sort: BLOCKERs -> HIGH -> MEDIUM -> LOW.

Print summary:

```
## Audit Summary — nai-planner

| Phase | Description | Findings |
|-------|-------------|----------|
| B | Static analysis | N |
| C | Models | N |
| D | DRF API | N |
| E | Ninja API | N |
| F | Security | N |
| G | Celery tasks | N |
| H | Code quality | N |
| I | Admin & signals | N |
| J | Dependencies | N |
| **Total** | | **N** |

Breakdown: X BLOCKER - Y HIGH - Z MEDIUM - W LOW

**HEALTHY** — 0 blockers, 0 high. Ship it.
or
**NEEDS WORK** — N blocker(s), M high(s) must be resolved.
```
