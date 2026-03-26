from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from nai_planner.models import PlannerItem


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def task_item(user):
    return PlannerItem.objects.create(
        user=user,
        item_type=PlannerItem.ItemType.TASK,
        title="Buy groceries",
        due_at=timezone.now() + timedelta(days=1),
    )


@pytest.fixture
def reminder_item(user):
    return PlannerItem.objects.create(
        user=user,
        item_type=PlannerItem.ItemType.REMINDER,
        title="Review note",
        due_at=timezone.now() + timedelta(hours=2),
        remind_at=timezone.now() + timedelta(hours=1),
    )


@pytest.fixture
def event_item(user):
    now = timezone.now()
    return PlannerItem.objects.create(
        user=user,
        item_type=PlannerItem.ItemType.EVENT,
        title="Team standup",
        due_at=now + timedelta(days=1),
        end_at=now + timedelta(days=1, minutes=30),
    )


class TestPlannerItemCreation:
    def test_create_task(self, task_item):
        assert task_item.item_type == "task"
        assert task_item.uuid is not None
        assert task_item.is_completed is False
        assert task_item.priority == "medium"

    def test_create_event_with_end_at(self, event_item):
        assert event_item.item_type == "event"
        assert event_item.end_at is not None
        assert event_item.end_at > event_item.due_at

    def test_create_reminder_with_remind_at(self, reminder_item):
        assert reminder_item.item_type == "reminder"
        assert reminder_item.remind_at is not None
        assert reminder_item.is_reminder_sent is False

    def test_str_representation(self, task_item):
        assert str(task_item) == "[task] Buy groceries"


class TestSoftDelete:
    def test_soft_delete_hides_from_default_manager(self, task_item):
        task_item.soft_delete()
        assert PlannerItem.objects.filter(uuid=task_item.uuid).count() == 0

    def test_soft_delete_visible_via_all_objects(self, task_item):
        task_item.soft_delete()
        assert PlannerItem.all_objects.filter(uuid=task_item.uuid).count() == 1

    def test_restore_after_soft_delete(self, task_item):
        task_item.soft_delete()
        assert PlannerItem.objects.filter(uuid=task_item.uuid).count() == 0
        task_item.restore()
        assert PlannerItem.objects.filter(uuid=task_item.uuid).count() == 1
        assert task_item.deleted_at is None


class TestOverdue:
    def test_not_overdue_when_future(self, task_item):
        assert task_item.is_overdue is False

    def test_overdue_when_past(self, user):
        item = PlannerItem.objects.create(
            user=user,
            item_type=PlannerItem.ItemType.TASK,
            title="Overdue task",
            due_at=timezone.now() - timedelta(hours=1),
        )
        assert item.is_overdue is True

    def test_not_overdue_when_completed(self, user):
        item = PlannerItem.objects.create(
            user=user,
            item_type=PlannerItem.ItemType.TASK,
            title="Done task",
            due_at=timezone.now() - timedelta(hours=1),
            is_completed=True,
        )
        assert item.is_overdue is False

    def test_not_overdue_when_no_due_at(self, user):
        item = PlannerItem.objects.create(
            user=user,
            item_type=PlannerItem.ItemType.TASK,
            title="No deadline",
        )
        assert item.is_overdue is False


class TestManagerFiltering:
    def test_default_manager_excludes_deleted(self, user):
        item1 = PlannerItem.objects.create(
            user=user, item_type="task", title="Active"
        )
        item2 = PlannerItem.objects.create(
            user=user, item_type="task", title="Deleted"
        )
        item2.soft_delete()

        active = PlannerItem.objects.filter(user=user)
        assert item1 in active
        assert item2 not in active

    def test_all_objects_includes_everything(self, user):
        item1 = PlannerItem.objects.create(
            user=user, item_type="task", title="Active"
        )
        item2 = PlannerItem.objects.create(
            user=user, item_type="task", title="Deleted"
        )
        item2.soft_delete()

        all_items = PlannerItem.all_objects.filter(user=user)
        assert item1 in all_items
        assert item2 in all_items
