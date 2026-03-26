from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Register the check_due_reminders periodic task in Celery Beat."

    def handle(self, *args, **options):
        try:
            from django_celery_beat.models import IntervalSchedule, PeriodicTask
        except ImportError:
            self.stderr.write(
                self.style.ERROR(
                    "django-celery-beat not installed. "
                    "Run: pip install nai-planner[celery]"
                )
            )
            return

        from nai_planner.conf import planner_settings

        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=planner_settings.reminder_check_interval_seconds,
            period=IntervalSchedule.SECONDS,
        )

        task, created = PeriodicTask.objects.get_or_create(
            name="nai_planner · check_due_reminders",
            defaults={
                "task": "nai_planner.check_due_reminders",
                "interval": schedule,
                "enabled": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created periodic task: {task.name} "
                    f"(every {schedule.every}s)"
                )
            )
        else:
            task.interval = schedule
            task.enabled = True
            task.save(update_fields=["interval", "enabled"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated periodic task: {task.name} "
                    f"(every {schedule.every}s)"
                )
            )
