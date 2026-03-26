---
name: dep-audit
description: "Dependency health audit for nai-planner pip package. Checks pyproject.toml for outdated, unused, vulnerable, or conflicting packages. Use when user says dep audit, dependency check, outdated packages, or package audit."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Dep Audit — Dependency Health Check

Audit every dependency in pyproject.toml for health, usage, and risk.

**RULE: Do NOT modify dependency files. Report only.**
**RULE: Check actual usage — do not trust package name alone.**

---

## Phase 1 — Read Dependencies

Read `pyproject.toml` and extract:
- Required dependencies (`[project.dependencies]`)
- Optional dependency groups: `drf`, `ninja`, `fcm`, `celery`, `all`, `dev`
- Build system requirements (`[build-system]`)

---

## Phase 2 — Outdated Check

```bash
pip list --outdated --format=columns 2>/dev/null | head -40
```

Flag:
- **HIGH:** Packages >2 major versions behind
- **MEDIUM:** Packages >1 major version behind
- **LOW:** Packages with minor/patch updates available

---

## Phase 3 — Unused Dependencies

For each package in dependencies, search for its import in `nai_planner/`:

**FAIL:** Package in dependencies but zero imports — likely unused
**WARN:** Package imported in only 1 file — verify it's needed

Skip known implicit deps: `django` itself, `setuptools`, build tools.

---

## Phase 4 — Version Constraints

**FAIL:**
- No version constraint (bare package name)
- `>=` without upper bound — could break on major update
- Git dependency pointing to `main`/`master` without commit hash

**WARN:**
- Overly tight constraint (`==1.2.3`) preventing security patches
- Optional dependency group without version constraints

---

## Phase 5 — Duplicate Functionality

Check for overlapping packages:
- Multiple REST frameworks (DRF + Ninja both optional, but check for conflicts)
- Multiple notification libraries

**WARN** for each overlap found — recommend consolidating.

---

## Phase 6 — Security & Risk

**FAIL:**
- Packages with known CVEs
- Packages last published >2 years ago with open security issues
- Archived/deprecated packages

**WARN:**
- Packages with no recent commits (>1 year)
- Packages maintained by single author

```bash
pip audit 2>/dev/null || echo "pip-audit not installed"
```

---

## Phase 7 — Django Compatibility

**FAIL:**
- Packages not compatible with Django >=4.2
- Packages using deprecated Django APIs

**WARN:**
- Packages that haven't declared Django 5.x support

---

## Phase 8 — Report

```
## Dep Audit — pyproject.toml

| # | Package | Version | Status | Issue | Severity |
|---|---------|---------|--------|-------|----------|

**Summary:**
- Required deps: N
- Optional deps: X
- Outdated: Y
- Unused: Z

Recommended actions:
1. [highest priority]
2. [second]
3. [third]
```
