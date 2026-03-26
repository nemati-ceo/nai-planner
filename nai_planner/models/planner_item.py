import uuid as _uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from nai_planner.conf import planner_settings


class PlannerItemManager(models.Manager):
    """Default manager that excludes soft-deleted items."""

    def get_queryset(self):
        qs = super().get_queryset()
        if planner_settings.soft_delete:
            return qs.filter(deleted_at__isnull=True)
        return qs


class AllItemsManager(models.Manager):
    """Manager that includes soft-deleted items."""
    pass


class PlannerItem(models.Model):

    class ItemType(models.TextChoices):
        TASK = "task", "Task"
        EVENT = "event", "Calendar Event"
        REMINDER = "reminder", "Reminder"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Recurrence(models.TextChoices):
        NONE = "none", "None"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    # Identity
    uuid = models.UUIDField(
        default=_uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planner_items",
    )

    # Core fields
    item_type = models.CharField(
        max_length=10,
        choices=ItemType.choices,
        db_index=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    # Generic link to any model (Note, Chat, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    linked_object = GenericForeignKey("content_type", "object_id")

    # Scheduling
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Deadline (task), event start (event), or target time (reminder).",
    )
    end_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Event end time. Only used for calendar events.",
    )
    remind_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When to fire the push notification. Can differ from due_at.",
    )
    is_all_day = models.BooleanField(default=False)
    recurrence = models.CharField(
        max_length=10,
        choices=Recurrence.choices,
        default=Recurrence.NONE,
        blank=True,
    )

    # Status
    is_completed = models.BooleanField(default=False, db_index=True)
    is_reminder_sent = models.BooleanField(
        default=False,
        help_text="Set to True after reminder push is dispatched.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Soft delete timestamp.",
    )

    # Managers
    objects = PlannerItemManager()
    all_objects = AllItemsManager()

    class Meta:
        ordering = ["-due_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["user", "item_type", "is_completed"],
                name="idx_planner_user_type_done",
            ),
            models.Index(
                fields=["remind_at", "is_reminder_sent"],
                name="idx_planner_remind_pending",
            ),
        ]
        verbose_name = "Planner Item"
        verbose_name_plural = "Planner Items"

    def __str__(self):
        return f"[{self.item_type}] {self.title}"

    def soft_delete(self):
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])

    @property
    def is_overdue(self) -> bool:
        if self.due_at and not self.is_completed:
            from django.utils import timezone
            return timezone.now() > self.due_at
        return False
