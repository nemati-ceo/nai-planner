# nai-planner

Reusable Django planner — tasks, calendar events, and reminders with GenericFK linking, Celery-powered reminders, and optional FCM push notifications.

## Architecture

Single model (`PlannerItem`) handles three item types:

| Type | Purpose | Key Fields |
|------|---------|------------|
| `task` | To-do items with deadlines | `due_at`, `priority`, `is_completed` |
| `event` | Calendar events with duration | `due_at`, `end_at`, `is_all_day` |
| `reminder` | Time-triggered notifications | `remind_at`, `is_reminder_sent` |

**GenericFK** — any item can link to any Django model (Note, Chat, Project, etc.) via `content_type` + `object_id`.

**Soft delete** — items are never hard-deleted. `deleted_at` timestamp hides them from default queries. Restore anytime.

**Managers** — `PlannerItem.objects` excludes soft-deleted items. `PlannerItem.all_objects` includes everything.

## Install

```bash
# Core only (models + signals + admin)
pip install nai-planner

# With Django REST Framework support
pip install nai-planner[drf]

# With Django Ninja support
pip install nai-planner[ninja]

# With FCM push notifications
pip install nai-planner[fcm]

# With Celery periodic tasks
pip install nai-planner[celery]

# Everything
pip install nai-planner[all]
```

## Quick Start

### 1. Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ...
    "nai_planner",
]
```

### 2. Run migrations

```bash
python manage.py migrate nai_planner
```

### 3. Wire up URLs

**DRF:**
```python
from nai_planner.contrib.drf.urls import urlpatterns as planner_urls

urlpatterns = [
    path("api/v1/", include(planner_urls)),
]
```

**Django Ninja:**
```python
from nai_planner.contrib.ninja.views import router as planner_router

api.add_router("/planner", planner_router)
```

### 4. Setup Celery Beat (optional)

```bash
python manage.py setup_planner_beat
```

### 5. Configure FCM (optional)

```python
# settings.py
NAI_PLANNER_FCM_ENABLED = True
NAI_PLANNER_FCM_CREDENTIALS_PATH = "/path/to/firebase-credentials.json"
NAI_PLANNER_FCM_TOKEN_GETTER = "myapp.utils.get_user_fcm_tokens"
```

The `FCM_TOKEN_GETTER` must be a dotted path to a callable: `callable(user) -> list[str]`

## API Endpoints

### DRF (ViewSet at `/api/v1/planner/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/planner/` | List user's items (filterable) |
| POST | `/planner/` | Create item |
| GET | `/planner/{uuid}/` | Get item detail |
| PUT/PATCH | `/planner/{uuid}/` | Update item |
| DELETE | `/planner/{uuid}/` | Soft delete item |
| POST | `/planner/{uuid}/complete/` | Mark as completed |
| POST | `/planner/{uuid}/restore/` | Restore soft-deleted item |

**Filters:** `?item_type=task`, `?priority=high`, `?is_completed=true`, `?due_after=2025-01-01`, `?due_before=2025-12-31`

### Ninja (Router)

Same endpoints at your configured path. All require authentication.

## Linking to Other Models

Link a planner item to any model using `linked_model` + `linked_object_id`:

```json
{
  "item_type": "task",
  "title": "Review meeting notes",
  "linked_model": "notes.Note",
  "linked_object_id": 42
}
```

Both fields are required together. The target model and object are validated on creation.

## Signals

```python
from django.dispatch import receiver
from nai_planner.signals import reminder_due

@receiver(reminder_due)
def handle_reminder(sender, user, item, **kwargs):
    # Send email, WebSocket, in-app notification, etc.
    pass
```

Fired when `remind_at <= now` and `is_reminder_sent=False`. The Celery task checks every 60 seconds (configurable).

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `NAI_PLANNER_FCM_ENABLED` | `False` | Enable FCM push for reminders |
| `NAI_PLANNER_FCM_CREDENTIALS_PATH` | `None` | Path to Firebase credentials JSON |
| `NAI_PLANNER_FCM_TOKEN_GETTER` | `None` | Dotted path to token getter callable |
| `NAI_PLANNER_REMINDER_CHECK_INTERVAL_SECONDS` | `60` | How often Celery checks for due reminders |
| `NAI_PLANNER_SOFT_DELETE` | `True` | Enable soft delete (deleted_at) |
| `NAI_PLANNER_USER_UUID_FIELD` | `"uuid"` | User model UUID field for API lookups |
| `NAI_PLANNER_DEFAULT_PRIORITY` | `"medium"` | Default priority for new items |

## Development

```bash
# Clone and install with dev deps
git clone https://github.com/NEMATI-AI/nai-planner.git
cd nai-planner
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check nai_planner/ tests/

# Format
ruff format nai_planner/ tests/
```

### Project Structure

```
nai_planner/
├── contrib/
│   ├── drf/               # DRF ViewSet, serializers, filters, URLs
│   └── ninja/             # Ninja router, schemas
├── management/commands/   # setup_planner_beat
├── migrations/            # Django migrations
├── models/                # PlannerItem model + managers
├── admin.py               # Django admin config
├── apps.py                # NaiPlannerConfig
├── conf.py                # Centralised settings (NAI_PLANNER_* prefix)
├── signals.py             # reminder_due signal
└── tasks.py               # Celery task + FCM push helper
tests/
├── settings.py            # SQLite in-memory test config
├── test_models.py         # Model + manager tests
└── test_tasks.py          # Celery task + signal tests
```

## License

MIT
