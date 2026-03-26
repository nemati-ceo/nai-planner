import logging

from django.utils import timezone

logger = logging.getLogger("nai_planner")


def _send_fcm_notification(item):
    """Optional FCM push. Only runs if firebase-admin is installed and configured."""
    from nai_planner.conf import planner_settings

    if not planner_settings.fcm_enabled:
        return

    try:
        from firebase_admin import messaging
    except ImportError:
        logger.warning("FCM enabled but firebase-admin not installed. pip install nai-planner[fcm]")
        return

    # Fetch device tokens — consuming app must provide this
    from django.conf import settings as django_settings
    from django.utils.module_loading import import_string

    token_getter_path = getattr(django_settings, "NAI_PLANNER_FCM_TOKEN_GETTER", None)
    if not token_getter_path:
        logger.warning(
            "NAI_PLANNER_FCM_TOKEN_GETTER not configured. "
            "Set it to a dotted path or callable(user) -> list[str]."
        )
        return

    try:
        token_getter = import_string(token_getter_path) if isinstance(token_getter_path, str) else token_getter_path
    except ImportError:
        logger.warning("Could not import %s", token_getter_path)
        return

    tokens = token_getter(item.user)
    if not tokens:
        logger.debug("No FCM tokens for user %s", item.user_id)
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=f"[{item.get_item_type_display()}] {item.title}",
            body=item.description[:200] if item.description else None,
        ),
        data={
            "planner_item_uuid": str(item.uuid),
            "item_type": item.item_type,
        },
        tokens=tokens,
    )
    response = messaging.send_each_for_multicast(message)
    logger.info(
        "FCM sent for item %s: %d success, %d failure",
        item.uuid,
        response.success_count,
        response.failure_count,
    )


try:
    from celery import shared_task

    @shared_task(name="nai_planner.check_due_reminders")
    def check_due_reminders():
        """
        Periodic task — runs every minute via Celery Beat.
        Finds items where remind_at <= now and is_reminder_sent=False,
        fires the reminder_due signal and optionally sends FCM push.
        """
        from nai_planner.models import PlannerItem
        from nai_planner.signals import reminder_due

        now = timezone.now()
        pending = PlannerItem.objects.filter(
            remind_at__lte=now,
            is_reminder_sent=False,
            is_completed=False,
        ).select_related("user")

        count = 0
        for item in pending:
            # Always fire the signal — consuming app decides what to do
            reminder_due.send(sender=PlannerItem, user=item.user, item=item)

            # Optional FCM push
            _send_fcm_notification(item)

            # Mark as sent
            item.is_reminder_sent = True
            item.save(update_fields=["is_reminder_sent", "updated_at"])
            count += 1

        if count:
            logger.info("Processed %d due reminders", count)

except ImportError:
    # Celery not installed — task won't be available
    pass
