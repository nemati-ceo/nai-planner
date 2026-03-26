from django.apps import AppConfig


class NaiPlannerConfig(AppConfig):
    name = "nai_planner"
    label = "nai_planner"
    verbose_name = "NAI Planner"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import nai_planner.signals  # noqa: F401
