from django.conf import settings


class PlannerSettings:
    """
    Centralised settings for nai-planner.
    Override any of these in your Django settings with the NAI_PLANNER_ prefix.
    """

    @property
    def fcm_enabled(self) -> bool:
        return getattr(settings, "NAI_PLANNER_FCM_ENABLED", False)

    @property
    def fcm_credentials_path(self) -> str | None:
        return getattr(settings, "NAI_PLANNER_FCM_CREDENTIALS_PATH", None)

    @property
    def reminder_check_interval_seconds(self) -> int:
        return getattr(settings, "NAI_PLANNER_REMINDER_CHECK_INTERVAL_SECONDS", 60)

    @property
    def soft_delete(self) -> bool:
        return getattr(settings, "NAI_PLANNER_SOFT_DELETE", True)

    @property
    def user_model_uuid_field(self) -> str:
        """Field name on User model used for API lookups (not PK)."""
        return getattr(settings, "NAI_PLANNER_USER_UUID_FIELD", "uuid")

    @property
    def default_priority(self) -> str:
        return getattr(settings, "NAI_PLANNER_DEFAULT_PRIORITY", "medium")


planner_settings = PlannerSettings()
