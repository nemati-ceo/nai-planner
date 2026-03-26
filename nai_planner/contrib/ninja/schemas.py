from datetime import datetime
from uuid import UUID

from ninja import Schema


class PlannerItemCreateSchema(Schema):
    item_type: str  # "task" | "event" | "reminder"
    title: str
    description: str = ""
    priority: str = "medium"
    due_at: datetime | None = None
    end_at: datetime | None = None
    remind_at: datetime | None = None
    is_all_day: bool = False
    recurrence: str = "none"
    linked_model: str | None = None  # "notes.Note"
    linked_object_id: int | None = None


class PlannerItemUpdateSchema(Schema):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    due_at: datetime | None = None
    end_at: datetime | None = None
    remind_at: datetime | None = None
    is_all_day: bool | None = None
    recurrence: str | None = None
    is_completed: bool | None = None


class PlannerItemOutSchema(Schema):
    uuid: UUID
    item_type: str
    title: str
    description: str
    priority: str
    due_at: datetime | None
    end_at: datetime | None
    remind_at: datetime | None
    is_all_day: bool
    recurrence: str
    is_completed: bool
    is_reminder_sent: bool
    is_overdue: bool
    content_type_id: int | None
    object_id: int | None
    created_at: datetime
    updated_at: datetime


class PlannerItemListSchema(Schema):
    uuid: UUID
    item_type: str
    title: str
    priority: str
    due_at: datetime | None
    is_all_day: bool
    is_completed: bool
    is_overdue: bool
    created_at: datetime
