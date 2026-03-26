---
name: release-check
description: "PyPI release readiness check for nai-planner. Verifies tests pass, version bumped, package builds, no debug artifacts, dependencies correct, changelog updated. Use when user says release check, ready to publish, release ready, publish check, or ship it."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Release Check — PyPI Publish Readiness

Final gate before publishing a new version to PyPI.

**RULE: Do NOT fix anything. Report only.**
**RULE: Execute every phase.**

---

## Phase 1 — Version Verification

Read `pyproject.toml` and `nai_planner/__init__.py`:

**BLOCKER:**
- Version in `pyproject.toml` does not match `__version__` in `__init__.py`
- Version not bumped since last release tag

```bash
git tag --sort=-v:refname | head -5
```

---

## Phase 2 — Test Suite

```bash
pytest --tb=short -q
```

**BLOCKER:** Any test failure.

**HIGH:**
- Tests with `@pytest.mark.skip`
- Missing tests for critical functionality (models, tasks, API endpoints)

---

## Phase 3 — Static Analysis

```bash
ruff check nai_planner/ tests/
```

**HIGH:** Any ruff error in package source.

---

## Phase 4 — Debug Artifacts

Scan `nai_planner/` for debug leftovers:

**BLOCKER:**
- `breakpoint()` or `import pdb`
- `print()` statements (use logger) — except in management commands
- `DEBUG = True` hardcoded

**HIGH:**
- `# TODO` or `# FIXME` on critical paths

---

## Phase 5 — Package Build

```bash
python -m build --sdist --wheel 2>&1 | tail -20
```

**BLOCKER:** Build failure.

Check package contents:
```bash
tar -tzf dist/*.tar.gz | head -30
```

**BLOCKER:**
- Missing `nai_planner/` package files
- `.env`, credentials, or test files included in distribution

---

## Phase 6 — pyproject.toml Audit

Read `pyproject.toml`:

**BLOCKER:**
- Missing required metadata (name, version, description, license)
- Missing Python version requirement
- Missing Django version requirement

**HIGH:**
- Dependencies without version constraints
- Missing classifiers (Django version, Python version, license)
- Missing `[project.urls]`

---

## Phase 7 — Security Scan

**BLOCKER:**
- Hardcoded secrets anywhere in `nai_planner/`
- Sensitive defaults in settings

```bash
pip audit 2>/dev/null || echo "pip-audit not installed"
```

---

## Phase 8 — Changelog & Documentation

**HIGH:**
- No CHANGELOG or release notes updated
- README not reflecting current features
- Settings table in README doesn't match conf.py

**WARN:**
- Missing migration guide for breaking changes

---

## Phase 9 — Git State

```bash
git status --short
git log --oneline -5
```

**BLOCKER:**
- Uncommitted changes
- Unpushed commits

**HIGH:**
- No git tag for the version being released

---

## Phase 10 — Report

```
## Release Check — nai-planner vX.Y.Z

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 1 | Version | PASS/FAIL | |
| 2 | Tests | PASS/FAIL | N passed, M failed |
| 3 | Static analysis | PASS/FAIL | |
| 4 | Debug artifacts | PASS/FAIL | N found |
| 5 | Package build | PASS/FAIL | |
| 6 | pyproject.toml | PASS/FAIL | |
| 7 | Security | PASS/FAIL | |
| 8 | Changelog | PASS/WARN | |
| 9 | Git state | PASS/FAIL | |

**Verdict:** READY TO PUBLISH / NOT READY — N blocker(s), M issue(s)
```
