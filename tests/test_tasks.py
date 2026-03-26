from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from nai_planner.models import PlannerItem
from nai_planner.signals import reminder_due


@pytest.fixture
def user(db):
    return User.objects.create_user(username="taskuser", password="testpass")


@pytest.fixture
def due_reminder(user):
    return PlannerItem.objects.create(
        user=user,
        item_type=PlannerItem.ItemType.REMINDER,
        title="Due now",
        remind_at=timezone.now() - timedelta(minutes=5),
        is_reminder_sent=False,
    )


@pytest.fixture
def future_reminder(user):
    return PlannerItem.objects.create(
        user=user,
        item_type=PlannerItem.ItemType.REMINDER,
        title="Future",
        remind_at=timezone.now() + timedelta(hours=2),
        is_reminder_sent=False,
    )


class TestCheckDueReminders:
    def test_signal_fires_for_due_reminders(self, due_reminder):
        handler = MagicMock()
        reminder_due.connect(handler)

        try:
            from nai_planner.tasks import check_due_reminders
            check_due_reminders()
        except ImportError:
            pytest.skip("Celery not installed")

        handler.assert_called_once()
        call_kwargs = handler.call_args[1]
        assert call_kwargs["item"].uuid == due_reminder.uuid
        assert call_kwargs["user"] == due_reminder.user

        reminder_due.disconnect(handler)

    def test_marks_reminder_as_sent(self, due_reminder):
        try:
            from nai_planner.tasks import check_due_reminders
            check_due_reminders()
        except ImportError:
            pytest.skip("Celery not installed")

        due_reminder.refresh_from_db()
        assert due_reminder.is_reminder_sent is True

    def test_ignores_future_reminders(self, future_reminder):
        handler = MagicMock()
        reminder_due.connect(handler)

        try:
            from nai_planner.tasks import check_due_reminders
            check_due_reminders()
        except ImportError:
            pytest.skip("Celery not installed")

        handler.assert_not_called()
        future_reminder.refresh_from_db()
        assert future_reminder.is_reminder_sent is False

        reminder_due.disconnect(handler)

    def test_ignores_already_sent(self, user):
        PlannerItem.objects.create(
            user=user,
            item_type=PlannerItem.ItemType.REMINDER,
            title="Already sent",
            remind_at=timezone.now() - timedelta(minutes=5),
            is_reminder_sent=True,
        )
        handler = MagicMock()
        reminder_due.connect(handler)

        try:
            from nai_planner.tasks import check_due_reminders
            check_due_reminders()
        except ImportError:
            pytest.skip("Celery not installed")

        handler.assert_not_called()
        reminder_due.disconnect(handler)

    def test_ignores_completed_items(self, user):
        PlannerItem.objects.create(
            user=user,
            item_type=PlannerItem.ItemType.REMINDER,
            title="Completed",
            remind_at=timezone.now() - timedelta(minutes=5),
            is_reminder_sent=False,
            is_completed=True,
        )
        handler = MagicMock()
        reminder_due.connect(handler)

        try:
            from nai_planner.tasks import check_due_reminders
            check_due_reminders()
        except ImportError:
            pytest.skip("Celery not installed")

        handler.assert_not_called()
        reminder_due.disconnect(handler)
