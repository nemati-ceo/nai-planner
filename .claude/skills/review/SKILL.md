---
name: review
description: "Quick code review on specific files. Checks Django model compliance, API safety, serializer validation, security, query performance, and code standards. Use when user says review, check this file, look at this, or code review."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Review — Targeted File Code Review

Senior Django engineer reviewing your files. Finding real issues, not style nits.

**RULE: Do NOT fix anything. Report only.**
**RULE: Read every file fully — do not skim.**

---

## Phase 1 — Identify Targets

If $ARGUMENTS provided, use those file paths.
If no arguments:

!`git diff --name-only HEAD~1`
!`git status --short`

Ask: "Which files should I review?" if still unclear.

---

## Phase 2 — Static Analysis

```bash
ruff check [target files]
```

---

## Phase 3 — Model Compliance

For target model files in `nai_planner/models/`:

**FAIL:**
- ForeignKey without explicit `on_delete`
- CharField without `max_length`
- Missing `__str__` method
- Soft delete logic gaps

**WARN:**
- Missing `db_index=True` on filtered fields
- Missing `verbose_name` on admin-visible fields

---

## Phase 4 — API View Safety

For DRF views in `nai_planner/contrib/drf/views.py`:

**FAIL:**
- Missing user isolation in get_queryset
- Missing permission_classes
- Hard delete instead of soft delete
- Custom actions not idempotent

For Ninja views in `nai_planner/contrib/ninja/views.py`:

**FAIL:**
- Same checks as DRF
- GenericFK resolution without error handling
- Missing authentication

---

## Phase 5 — Serializer & Schema Review

For DRF serializers:

**FAIL:**
- Sensitive internal fields exposed
- Missing validation on linked_model format
- Read-only fields not marked

For Ninja schemas:

**FAIL:**
- Inconsistent fields with DRF serializers
- Missing optional field handling

---

## Phase 6 — Celery Task Patterns

For target task files:

**FAIL:**
- Tasks without error handling
- Tasks making external calls without timeout
- Per-item saves instead of bulk_update

---

## Phase 7 — Query Performance

**FAIL:**
- N+1 queries (related access in loops without `select_related`/`prefetch_related`)

**WARN:**
- Missing `db_index` on frequently filtered fields
- Missing `select_related`/`prefetch_related` on FK access

---

## Phase 8 — Security

**FAIL:**
- Raw SQL with f-strings/string formatting
- Hardcoded secrets, API keys, tokens
- `eval()`/`exec()` on user input
- User-controlled input in `.filter(**kwargs)` via dict expansion
- Sensitive data in log output

---

## Phase 9 — Code Standards

Per CLAUDE.md: max 200 lines per file and per function/class.

**FAIL:**
- File over 200 lines
- Function over 200 lines
- `print()` in production code
- `breakpoint()` or `pdb` imports
- Silent catch blocks

**WARN:**
- Approaching 200-line limit (180+)
- Magic strings/numbers

---

## Phase 10 — Report

```
## Review — [file name(s)]

| # | File:Line | Issue | Severity |
|---|-----------|-------|----------|

**Verdict:** CLEAN / N issue(s) found
```

If CLEAN: "No issues. Ship it."
If issues: list fixes, suggest `/redo [filename]` after fixing.
