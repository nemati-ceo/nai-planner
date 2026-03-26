---
name: resume
description: "Resume a paused task by rebuilding full project context. Reads the active plan,
recent git history, todo/issues files, and CLAUDE.md to produce a status
summary and the next action. Use when returning after a break or when the
user says resume, continue, where was I, pick up, or what's next."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Resume — Rebuild Context & Continue

The user left mid-task. Reconstruct where they stopped and tell them the ONE next thing.

**RULE: Do NOT start working. Report status only.**
**RULE: Read every source — do not guess.**

---

## Phase 1 — Load Project Context

!`cat CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"`

**Stack:** nai-planner — pip-installable Django planner package
- Django >=4.2
- Optional: djangorestframework, django-ninja, firebase-admin, celery + django-celery-beat
- Python >=3.10
- Tests: pytest + pytest-django, SQLite in-memory
- Source: `nai_planner/`
- Tests: `tests/`

Commands:
- Test: `pytest`
- Lint: `ruff check nai_planner/ tests/`
- Check: `DJANGO_SETTINGS_MODULE=tests.settings python -m django check`
- Build: `python -m build`

---

## Phase 2 — Find the Active Plan

!`ls -t docs/plans/*.md 2>/dev/null | head -5`

If $ARGUMENTS provided, use that to locate the plan.

Read the most recent plan. Parse for:
- **Task title/goal**
- **Phases/steps**
- **Completed items** (`- [x]`)
- **Incomplete items** (`- [ ]`)
- **Current phase** — first phase with `- [ ]`

If no plan: "No plan file found. Using git history only."

---

## Phase 3 — Recent Git Activity

!`git log --oneline -15`
!`git diff --stat HEAD~5 2>/dev/null || git diff --stat`
!`git status --short`

Extract:
- Last 5 commit messages
- Uncommitted changes (work in progress)
- Untracked files

---

## Phase 4 — Open Issues / TODOs

!`cat docs/issues.md 2>/dev/null || echo ""`
!`cat TODO.md 2>/dev/null || echo ""`

Scan recently changed files for inline markers:
!`git diff --name-only HEAD~5 2>/dev/null | head -20 | xargs grep -n "TODO\|FIXME\|HACK" 2>/dev/null | head -20`

---

## Phase 5 — Determine Next Action

Using everything above, identify:
1. **Current phase** from the plan
2. **Next incomplete task**
3. **Blockers** — uncommitted WIP, failing tests, unresolved TODOs
4. **Files that will be touched**

---

## Phase 6 — Output

```
## Resume — nai-planner

**Package:** nai-planner (pip-installable Django planner package)
**Plan:** [filename] — [goal]

### Progress

| Phase | Status | Detail |
|-------|--------|--------|
| Phase 1 — [name] | Done | [completed] |
| Phase 2 — [name] | In Progress | [X of Y done] |

### Recent Activity

Last commits:
- [message 1]
- [message 2]
- [message 3]

Uncommitted changes: [N files] — [key files]

### Open Items

- [TODOs/FIXMEs]
- [incomplete items from docs/issues.md]

### Next Action

**[Phase N, Task name]**
[One clear sentence describing exactly what to do next.]
Files to touch: `path/to/file1`, `path/to/file2`
```

---

## Edge Cases

**No plan, no todo:** Use git history. Ask user to confirm direction.
**Multiple plans:** Use most recent. Suggest `/resume [filename]` for alternatives.
**Everything complete:** "All done. Run `/validate` then `/pre-commit`."
**Dirty working tree:** Flag uncommitted changes.
