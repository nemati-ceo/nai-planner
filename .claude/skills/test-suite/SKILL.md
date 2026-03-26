---
name: test-suite
description: "Generate and run comprehensive tests for nai-planner before PyPI publish. Analyzes untested modules, creates missing tests, runs full suite, reports coverage. Use when user says test suite, generate tests, test everything, cover all, or test before publish."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# Test Suite — Generate & Verify All Tests

Find untested code, generate missing tests, run the full suite, and prove the package works.

**RULE: Show generated test code BEFORE writing — get user approval.**
**RULE: Tests go in `tests/` directory following existing patterns.**
**RULE: Use pytest + pytest-django with `tests/settings.py`.**
**RULE: Never mock what you can test directly — use real SQLite in-memory DB.**

---

## Phase 1 — Inventory: What Exists

Map every testable module in `nai_planner/`:

!`find nai_planner -name '*.py' -not -path '*/__pycache__/*' -not -path '*/migrations/*'`
!`ls tests/test_*.py`

Build a coverage matrix:

| Module | Test File | Status |
|--------|-----------|--------|
| `models/planner_item.py` | `tests/test_models.py` | EXISTS / MISSING |
| `contrib/drf/views.py` | `tests/test_drf_views.py` | EXISTS / MISSING |
| `contrib/drf/serializers.py` | `tests/test_drf_serializers.py` | EXISTS / MISSING |
| `contrib/ninja/views.py` | `tests/test_ninja_views.py` | EXISTS / MISSING |
| `admin.py` | `tests/test_admin.py` | EXISTS / MISSING |
| `tasks.py` | `tests/test_tasks.py` | EXISTS / MISSING |
| `signals.py` | `tests/test_signals.py` | EXISTS / MISSING |
| `conf.py` | `tests/test_conf.py` | EXISTS / MISSING |
| `management/commands/*.py` | `tests/test_commands.py` | EXISTS / MISSING |

---

## Phase 2 — Coverage Gap Analysis

For each EXISTING test file, read it and check:

- Which functions/classes/methods are tested
- Which are NOT tested (compare against source module)
- Which edge cases are missing

For each module WITHOUT a test file:

- List every public function, class, and method that needs tests
- Flag critical code that MUST have tests (user isolation, soft delete, reminders)

Output:

```
## Coverage Gaps

| Module | Public Functions | Tested | Untested | Priority |
|--------|-----------------|--------|----------|----------|
```

Priority: HIGH = API user isolation/tasks, MEDIUM = models/admin, LOW = config/helpers

---

## Phase 3 — Generate Missing Tests

For each gap identified, generate test code following these patterns:

**What to test per module type:**

**Models** — creation, validation, `__str__`, soft delete, restore, is_overdue, managers
**DRF Views** — CRUD, user isolation, soft delete on destroy, complete/restore actions, filtering
**DRF Serializers** — validation (linked_model, end_at for non-events), read-only fields
**Ninja Views** — CRUD, user isolation, GenericFK resolution, error handling
**Admin** — registration, list_display fields exist, search_fields, filters
**Tasks** — due reminders processed, future/sent/completed ignored, signal fires, FCM mocked
**Signals** — signal defined, can connect handler
**Config** — default values, override via settings
**Management commands** — runs without error, handles missing celery-beat

**RULE: Mock external dependencies (firebase-admin, celery-beat) — NOT Django internals.**
**RULE: Use `@override_settings()` to test different configuration scenarios.**

---

## Phase 4 — Present for Approval

Show the user:

1. Which test files will be **created** (new)
2. Which test files will be **extended** (existing, new test methods)
3. The full test code for each file

**STOP HERE — wait for user approval before writing any files.**

---

## Phase 5 — Write Tests

After approval, write/update test files in `tests/`.

- New files: `tests/test_<module>.py`
- Extended files: append new test classes/methods to existing files
- Keep each test file under 200 lines — split if needed

---

## Phase 6 — Run Full Suite

```bash
pytest --tb=short -v
```

If failures:
1. Show each failure with file:line and traceback
2. Diagnose the root cause (test bug vs code bug)
3. If test bug: propose fix and ask user
4. If code bug: flag it — do NOT fix production code, report only

---

## Phase 7 — Coverage Report (if pytest-cov available)

```bash
pytest --cov=nai_planner --cov-report=term-missing --tb=short -q 2>/dev/null
```

If pytest-cov not installed, skip and note: "Install `pytest-cov` for coverage metrics."

---

## Phase 8 — Report

```
## Test Suite — nai-planner

| Module | Tests Before | Tests After | Status |
|--------|-------------|-------------|--------|

**Results:** N passed, M failed, K skipped

**Coverage:** X% (if available)

**Verdict:** ALL GREEN / N failure(s) remaining
```
