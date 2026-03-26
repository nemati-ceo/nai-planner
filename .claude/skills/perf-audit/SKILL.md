---
name: perf-audit
description: "Performance audit for nai-planner Django package. Checks query optimization, N+1 patterns, indexing, Celery task efficiency, and serializer overhead. Use when user says perf audit, performance, slow, optimize, or query optimization."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Perf Audit — Performance Review

Find every performance problem. No compliments, only issues.

**RULE: Do NOT fix anything. Report only.**
**RULE: Read actual file contents — do not guess.**

---

## Phase 1 — Scope

If $ARGUMENTS provided, scope to those paths.
Otherwise, audit all of `nai_planner/`.

---

## Phase 2 — Query Performance

Scan `nai_planner/models/` and `nai_planner/contrib/`:

**FAIL:**
- Queryset access inside a loop without `select_related`/`prefetch_related`
- `.all()` or `.filter()` called inside loops (N+1)
- `Model.objects.get()` inside a loop
- Queryset evaluated multiple times (not cached in variable)

**WARN:**
- Large querysets without `.iterator()` (memory pressure)
- Missing `values()` or `values_list()` when only specific fields needed
- `.exists()` not used where only existence check needed

---

## Phase 3 — Indexing

Scan model definitions:

**FAIL:**
- Fields used in `filter()`, `exclude()`, `order_by()` without `db_index=True`
- Missing composite indexes for multi-field lookups

Cross-reference indexes with query patterns:
- `idx_planner_user_type_done` — covers user + item_type + is_completed
- `idx_planner_remind_pending` — covers remind_at + is_reminder_sent
- `deleted_at` has `db_index=True` — used by soft delete manager
- Missing: `user` + `due_at` for calendar range queries?

---

## Phase 4 — N+1 Detection in Views

Read all view/viewset files:
- `nai_planner/contrib/drf/views.py` — does `get_queryset` use `select_related`?
- `nai_planner/contrib/ninja/views.py` — same check
- `nai_planner/admin.py` — does `list_display` cause N+1 on `user` FK?

Key concern: `user` FK in list views without `select_related`.

---

## Phase 5 — Celery Task Performance

Read `nai_planner/tasks.py`:

**FAIL:**
- `check_due_reminders` processes items one-by-one with individual saves
- Could use `bulk_update` instead of per-item `save()`
- FCM tokens fetched per-item instead of batched

**WARN:**
- No `soft_time_limit` on task
- Missing `.iterator()` for large result sets

---

## Phase 6 — Serializer Performance

Read `nai_planner/contrib/drf/serializers.py`:

- `is_overdue` is a property — causes per-row computation in list view
- `content_type` FK in serializer — extra query per item if not select_related
- List serializer vs detail serializer — is list serializer lean enough?

---

## Phase 7 — Report

```
## Perf Audit — nai-planner

| # | File:Line | Issue | Category | Severity |
|---|-----------|-------|----------|----------|

**Summary:** N issues (X FAIL, Y WARN)

Top 3 impact fixes:
1. [highest impact]
2. [second]
3. [third]
```
