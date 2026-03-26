# Plan: Integrate nai-planner into nai_backend

**Date:** 2026-03-25
**Status:** PENDING APPROVAL
**Target repo:** d:\NAI_Project\BACKENDS\nai_backend

---

## Pre-Integration Assessment

### What exists in nai_backend already
- **Celery + Beat**: Configured with Redis broker, DatabaseScheduler — production-ready
- **Firebase Admin SDK**: Lazy-init from `FIREBASE_SERVICE_ACCOUNT_BASE64` env var (`core/firebase/__init__.py`)
- **DRF**: `djangorestframework==3.16.0` + `django-filter==25.2` installed, `rest_framework` in INSTALLED_APPS
- **django-celery-beat**: `==2.8.1` installed, in INSTALLED_APPS
- **User model**: `apps.user.models.User` with `uuid = UUIDField` (matches nai-planner default)
- **AUTH_USER_MODEL**: `"user.User"`
- **URL prefix**: `auth/api/v1/` (Ninja catch-all at this prefix)

### What does NOT exist
- No device token / FCM registration model — only topic-based FCM via `apps.blog`
- No planner, task, calendar, or reminder app
- No `nai-planner` in requirements

### Critical integration points
1. **FCM init**: nai-planner calls `firebase_admin.messaging` directly (uses default app). nai_backend lazy-inits Firebase only when `get_firebase_app()` is called. Must ensure Firebase is initialized before Celery task runs.
2. **FCM tokens**: `NAI_PLANNER_FCM_TOKEN_GETTER` requires `callable(user) -> list[str]`. No device token model exists — must create one or defer FCM.
3. **URL routing**: DRF urls must be placed BEFORE the Ninja catch-all in `core/urls.py`.

---

## Phase 1: Install & Configure

### 1.1 Install package
```bash
pip install nai-planner[drf,celery,fcm]
```
Then add to `requirements/requirements.txt`:
```
nai-planner[drf,celery,fcm]==0.1.0
```

### 1.2 Add to INSTALLED_APPS
**File:** `core/settings/base.py`

Add `"nai_planner"` after `"django.contrib.contenttypes"` in INSTALLED_APPS:
```python
"django.contrib.contenttypes",
"nai_planner",  # Planner: tasks, events, reminders
```

### 1.3 Add NAI_PLANNER_* settings
**File:** `core/settings/base.py` (append after existing app configs)

```python
# ── nai-planner ──────────────────────────────────────────
NAI_PLANNER_FCM_ENABLED = False          # Phase 4 enables this
NAI_PLANNER_SOFT_DELETE = True
NAI_PLANNER_DEFAULT_PRIORITY = "medium"
NAI_PLANNER_REMINDER_CHECK_INTERVAL_SECONDS = 60
# NAI_PLANNER_FCM_TOKEN_GETTER = ...     # Phase 4
```

### 1.4 Run migrations
```bash
python manage.py migrate nai_planner
```

### 1.5 Verify
```bash
python manage.py showmigrations nai_planner
```
**Expected:** `[X] 0001_initial`

### Files modified
| File | Action |
|------|--------|
| `requirements/requirements.txt` | Add nai-planner line |
| `core/settings/base.py` | Add to INSTALLED_APPS + planner settings block |

---

## Phase 2: Wire URLs

### 2.1 Add DRF URL include
**File:** `core/urls.py`

Add BEFORE the Ninja catch-all line (`path("auth/api/v1/", api.urls)`):
```python
path("auth/api/v1/", include("nai_planner.contrib.drf.urls")),
```

This registers:
```
GET    auth/api/v1/planner/                  # List (filterable)
POST   auth/api/v1/planner/                  # Create
GET    auth/api/v1/planner/{uuid}/           # Retrieve
PUT    auth/api/v1/planner/{uuid}/           # Update
PATCH  auth/api/v1/planner/{uuid}/           # Partial update
DELETE auth/api/v1/planner/{uuid}/           # Soft delete
POST   auth/api/v1/planner/{uuid}/complete/  # Mark complete
POST   auth/api/v1/planner/{uuid}/restore/   # Restore soft-deleted
```

**Why before Ninja?** Django URL resolution is first-match. The Ninja `api.urls` catches everything under `auth/api/v1/`. DRF routes must be tried first so `/planner/` doesn't 404 in Ninja.

### 2.2 Verify
```bash
python manage.py show_urls | grep planner
```
**Expected:** 8 planner endpoints listed.

If `show_urls` not available:
```bash
python manage.py check
```

### Files modified
| File | Action |
|------|--------|
| `core/urls.py` | Add 1 line (DRF include) |

---

## Phase 3: Celery Beat Setup

### 3.1 Register periodic task
```bash
python manage.py setup_planner_beat
```

This creates:
- `IntervalSchedule`: every 60 seconds
- `PeriodicTask`: `"nai_planner · check_due_reminders"` → `"nai_planner.check_due_reminders"`

### 3.2 Verify
```bash
python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
pt = PeriodicTask.objects.filter(name__contains='nai_planner')
for t in pt: print(f'{t.name} | enabled={t.enabled} | interval={t.interval}')
"
```
**Expected:** 1 task, enabled, 60-second interval.

### Files modified
None — database-only operation.

---

## Phase 4: Connect FCM Token Getter

### DECISION NEEDED: Device token storage

**Option A — Create a DeviceToken model (recommended)**
New file: `apps/notifications/models/device_token.py` (< 40 lines)
```python
class DeviceToken(models.Model):
    user = ForeignKey(User, CASCADE, related_name="device_tokens")
    token = CharField(max_length=512, unique=True)
    platform = CharField(choices=[("ios","iOS"),("android","Android"),("web","Web")])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
```
Plus a registration API endpoint and the token getter callable.

**Option B — Defer FCM, use signal only**
Keep `NAI_PLANNER_FCM_ENABLED = False`. Wire the `reminder_due` signal to the existing `apps.notification_system` (Apprise-based multi-channel: email, Slack, Telegram). Add FCM later when a device token model exists.

### 4.1 (If Option A) Create FCM token getter
**File:** `apps/notifications/planner_fcm.py` (< 30 lines)

```python
def get_fcm_tokens(user):
    """Return active FCM device tokens for a user."""
    from apps.notifications.models.device_token import DeviceToken
    return list(
        DeviceToken.objects.filter(user=user, is_active=True)
        .values_list("token", flat=True)
    )
```

### 4.2 (If Option A) Update settings
**File:** `core/settings/base.py`
```python
NAI_PLANNER_FCM_ENABLED = True
NAI_PLANNER_FCM_TOKEN_GETTER = "apps.notifications.planner_fcm.get_fcm_tokens"
```

**WAIT** — nai-planner's `tasks.py:24` does `getattr(django_settings, "NAI_PLANNER_FCM_TOKEN_GETTER", None)` then checks `callable(token_getter)`. A string path is NOT callable. This is a **bug in nai-planner** — it should resolve dotted paths to callables.

**Fix required in nai-planner** (before Phase 4 can work):
Either:
- nai-planner must resolve string paths via `django.utils.module_loading.import_string`
- OR nai_backend must assign the actual callable (not a string) in settings

The simplest fix: update `tasks.py` in nai-planner to handle string paths.

### 4.3 Ensure Firebase is initialized before task runs
**File:** `apps/notifications/planner_fcm.py` — the token getter should also init Firebase:
```python
from core.firebase import get_firebase_app
# Call at module level or inside the function
```

Or better: call `get_firebase_app()` in `core/celery.py` after app config:
```python
@app.on_after_configure.connect
def init_firebase(**kwargs):
    from core.firebase import get_firebase_app
    get_firebase_app()
```

### 4.4 Wire reminder_due signal
**File:** `apps/notifications/signals/planner_handlers.py` (< 30 lines)

```python
from django.dispatch import receiver
from nai_planner.signals import reminder_due

@receiver(reminder_due)
def handle_planner_reminder(sender, user, item, **kwargs):
    # Route to existing notification system
    from apps.notifications.tasks import send_notification_email_task
    send_notification_email_task.delay(
        user_id=user.id,
        template_name="planner_reminder",
        context={"title": item.title, "item_type": item.item_type},
    )
```

### Files modified/created (Option A)
| File | Action |
|------|--------|
| `apps/notifications/models/device_token.py` | Create |
| `apps/notifications/planner_fcm.py` | Create |
| `apps/notifications/signals/planner_handlers.py` | Create |
| `apps/notifications/apps.py` | Modify (import signal handlers in ready()) |
| `core/settings/base.py` | Modify (enable FCM settings) |
| `core/celery.py` | Modify (add Firebase init hook) |

### Files modified (Option B — signal only)
| File | Action |
|------|--------|
| `apps/notifications/signals/planner_handlers.py` | Create |
| `apps/notifications/apps.py` | Modify (import signal handlers in ready()) |

---

## Phase 5: Verify End-to-End

### 5.1 Django system check
```bash
python manage.py check --deploy
```

### 5.2 Migration consistency
```bash
python manage.py migrate --check
```

### 5.3 Smoke test — Create a planner item
```bash
curl -X POST http://localhost:8000/auth/api/v1/planner/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "item_type": "task",
    "title": "Integration test task",
    "priority": "high",
    "due_at": "2026-03-26T10:00:00Z"
  }'
```
**Expected:** 201 Created with UUID in response.

### 5.4 Smoke test — List planner items
```bash
curl http://localhost:8000/auth/api/v1/planner/?item_type=task \
  -H "Authorization: Bearer <TOKEN>"
```
**Expected:** 200 OK with paginated list including the item above.

### 5.5 Smoke test — Complete & Restore
```bash
curl -X POST http://localhost:8000/auth/api/v1/planner/<UUID>/complete/ \
  -H "Authorization: Bearer <TOKEN>"
curl -X POST http://localhost:8000/auth/api/v1/planner/<UUID>/restore/ \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Known Issue: nai-planner FCM_TOKEN_GETTER bug

**File:** `nai_planner/tasks.py:24-25`
```python
token_getter = getattr(django_settings, "NAI_PLANNER_FCM_TOKEN_GETTER", None)
if not callable(token_getter):
```

This expects a callable object in Django settings, but Django settings typically use dotted string paths (e.g., `"apps.notifications.planner_fcm.get_fcm_tokens"`). A string is not callable.

**Fix needed in nai-planner before Phase 4:**
```python
from django.utils.module_loading import import_string

token_getter = getattr(django_settings, "NAI_PLANNER_FCM_TOKEN_GETTER", None)
if isinstance(token_getter, str):
    token_getter = import_string(token_getter)
if not callable(token_getter):
    ...
```

This fix should be done in the nai-planner repo first, then a new version published.

---

## Execution Order

```
Phase 1 → Phase 2 → Phase 3 → Phase 5 (verify without FCM)
                                  ↓
                        Fix nai-planner FCM bug
                                  ↓
                              Phase 4 → Phase 5 (verify with FCM)
```

Phases 1-3 + 5 can proceed immediately. Phase 4 is blocked on:
1. Decision: Option A vs Option B
2. nai-planner FCM_TOKEN_GETTER bug fix (if Option A)

---

## Summary of all files touched in nai_backend

| File | Phase | Action |
|------|-------|--------|
| `requirements/requirements.txt` | 1 | Modify — add nai-planner |
| `core/settings/base.py` | 1, 4 | Modify — INSTALLED_APPS + planner settings |
| `core/urls.py` | 2 | Modify — add DRF include (1 line) |
| `core/celery.py` | 4A | Modify — Firebase init hook (4 lines) |
| `apps/notifications/models/device_token.py` | 4A | Create (< 40 lines) |
| `apps/notifications/planner_fcm.py` | 4A | Create (< 30 lines) |
| `apps/notifications/signals/planner_handlers.py` | 4 | Create (< 30 lines) |
| `apps/notifications/apps.py` | 4 | Modify — import handlers in ready() |

**Total new files:** 2-3 (all under 40 lines)
**Total modified files:** 3-5 (minimal changes each)
