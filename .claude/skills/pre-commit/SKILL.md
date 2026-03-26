---
name: pre-commit
description: "Pre-push quality and security gate for nai-planner. Audits staged changes for secrets, SQL injection, security gaps, code standards, and test integrity. Use when user says pre-commit, pre-push, audit changes, review before push, check my code, or gate check."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Pre-Commit Audit — nai-planner

Paranoid security-conscious review before code leaves this machine.

**RULE: Do NOT fix anything. Report only.**
**RULE: Execute every phase in order.**

---

## Phase 1 — Gather Scope

!`git diff --cached --name-only`
!`git diff --cached --stat`
!`git status --short`

If $ARGUMENTS provided, scope to those files only.
If no files staged, check uncommitted changes instead.

Store the list of changed `.py` files as audit targets.

---

## Phase 2 — Static Analysis

```bash
pytest --tb=short -q
ruff check nai_planner/ tests/
```

- Any test failure -> **FAIL**
- Any ruff error -> **FAIL**

---

## Phase 3 — Secrets & Credential Scan

For each changed file, scan for:

**FAIL (block push):**
- API keys, tokens, passwords hardcoded (not from env/settings)
- Patterns: `AKIA[0-9A-Z]{16}`, `sk-[a-zA-Z0-9]{20,}`, `ghp_[a-zA-Z0-9]{36}`
- `password\s*=\s*["'][^"']+["']` (hardcoded passwords)
- Firebase credentials JSON paths pointing to real files
- Private keys: `-----BEGIN.*PRIVATE KEY-----`
- `SECRET_KEY` hardcoded in any file
- `.env` files staged for commit

---

## Phase 4 — Security Audit

For each changed `.py` file:

**FAIL:**
- Raw SQL with string formatting/f-strings (SQL injection)
- `eval()`, `exec()`, `__import__()` on user input
- `mark_safe()` on user input (XSS)
- Shell commands with user input (`subprocess`, `os.system` with f-strings)
- Sensitive data in response/error messages
- User-controlled input in `.filter(**kwargs)` via dict expansion
- GenericFK resolution without input validation

**WARN:**
- Broad exception catching without logging
- Sensitive data in error responses

---

## Phase 5 — Model & API Audit

For changed model files in `nai_planner/models/`:

**FAIL:**
- ForeignKey without `on_delete`
- CharField without `max_length`
- Soft delete logic gaps

For changed API files in `nai_planner/contrib/`:

**FAIL:**
- Missing user isolation (user filter in queryset)
- Missing permission_classes
- Missing input validation

---

## Phase 6 — Celery Task Safety

For changed task files:

**FAIL:**
- Tasks without error handling
- Tasks making external calls without timeout
- FCM push without failure handling

**WARN:**
- Missing `max_retries`, `acks_late`, or `time_limit`

---

## Phase 7 — Code Standards

Per CLAUDE.md: max 200 lines per file and per function/class.

**FAIL:**
- File over 200 lines
- Function/method over 200 lines
- `breakpoint()` or `pdb` imports
- `print()` statements (use logger)
- Hard-coded URLs, IPs, or API base URLs
- Silent catch blocks

**WARN:**
- Approaching 200-line limit (180+)
- Magic strings/numbers not in constants
- TODO/FIXME/HACK without linked issue
- Commented-out code blocks (>3 lines)
- Unused imports

---

## Phase 8 — Migration Check

```bash
DJANGO_SETTINGS_MODULE=tests.settings python -m django makemigrations --check --dry-run 2>/dev/null
```

**FAIL:**
- Model changes without corresponding migration

---

## Phase 9 — Report

```
## Pre-Commit Audit — nai-planner

| # | Phase | Result | Findings |
|---|-------|--------|----------|
| 1 | Static analysis | PASS/FAIL | N issues |
| 2 | Secrets scan | PASS/FAIL | N issues |
| 3 | Security | PASS/FAIL | N issues |
| 4 | Models & API | PASS/FAIL | N issues |
| 5 | Celery tasks | PASS/FAIL/SKIP | N issues |
| 6 | Code standards | PASS/FAIL | N issues |
| 7 | Migrations | PASS/FAIL | N issues |
```

### Hard Fails

For each:
1. **File:Line** — exact location
2. **Rule** — which rule violated
3. **Evidence** — offending snippet (max 3 lines)
4. **Fix** — exact change needed

### Verdict

**APPROVED** — all phases pass. Safe to push.

or

**BLOCKED** — N hard fail(s) must be resolved.
Priority: security > models > code standards > other.
