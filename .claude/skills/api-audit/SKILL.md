---
name: api-audit
description: "Library API surface audit for nai-planner Django package. Checks public exports, model fields, DRF/Ninja API, admin configuration, settings, and management commands. Use when user says api audit, check exports, api review, interface check, or public API audit."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# API Audit — Library Interface Review

Audit the public API surface of the nai-planner package.

**RULE: Do NOT fix anything. Report only.**
**RULE: Read actual file contents — do not guess.**

---

## Phase 1 — Scope

Read `nai_planner/__init__.py` to see public exports.

If $ARGUMENTS provided, scope to those modules only.
Otherwise, audit the entire `nai_planner/` package.

---

## Phase 2 — Public Exports

Check `nai_planner/__init__.py` and `nai_planner/models/__init__.py`:

**FAIL:**
- Internal classes/functions exported publicly (prefixed with `_`)
- Missing `__all__` definition in models
- Importing private modules in public API

**WARN:**
- Version string not defined or inconsistent with pyproject.toml

---

## Phase 3 — Model API

Read `nai_planner/models/planner_item.py`:

**FAIL:**
- ForeignKey without explicit `on_delete`
- CharField without `max_length`
- Missing `__str__` method
- Choices classes not using TextChoices properly

**WARN:**
- Missing `db_index=True` on fields likely used in lookups
- Missing `verbose_name` on fields exposed in admin
- Missing `help_text` on configurable fields

---

## Phase 4 — DRF Integration

Read `nai_planner/contrib/drf/`:

**FAIL:**
- Serializer exposing internal fields (id, content_type raw FK)
- Missing validation on linked_model format
- ViewSet missing permission_classes
- User isolation not enforced in get_queryset

**WARN:**
- Missing documentation for custom actions (complete, restore)
- List serializer too heavy (should be lightweight)
- Filters missing common query patterns

---

## Phase 5 — Ninja Integration

Read `nai_planner/contrib/ninja/`:

**FAIL:**
- Schema fields inconsistent with DRF serializer fields
- Missing authentication enforcement
- GenericFK resolution without proper error handling

**WARN:**
- Missing response schema for error cases
- Inconsistent field naming between DRF and Ninja

---

## Phase 6 — Admin Configuration

Read `nai_planner/admin.py`:

**FAIL:**
- Sensitive fields shown in list_display
- Missing `readonly_fields` on auto-generated fields
- Admin actions that modify data without confirmation

**WARN:**
- Missing `search_fields` or `list_filter`
- Missing `ordering` on ModelAdmin

---

## Phase 7 — Configuration & Settings

Read `nai_planner/conf.py`:

**FAIL:**
- Required settings without clear error messages when missing
- Settings read at import time instead of at runtime (breaks lazy config)
- Missing settings that code references

**WARN:**
- Inconsistent setting name patterns
- Settings not documented in README.md

---

## Phase 8 — Management Commands

Read `nai_planner/management/commands/`:

**FAIL:**
- Commands without `help` attribute
- Commands that fail silently on error
- Hard-coded values that should be configurable

**WARN:**
- Missing `add_arguments` for configurable behavior

---

## Phase 9 — Report

```
## API Audit — nai-planner

| # | Module | Issue | Severity |
|---|--------|-------|----------|

**Summary:**
- Public exports: N
- Models: Y
- DRF endpoints: Z
- Ninja endpoints: W

Issues: A FAIL, B WARN

Top 3 priority fixes:
1. [highest priority]
2. [second]
3. [third]
```
