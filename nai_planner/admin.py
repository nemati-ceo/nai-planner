from django.contrib import admin

from nai_planner.models import PlannerItem


@admin.register(PlannerItem)
class PlannerItemAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "user",
        "item_type",
        "title",
        "priority",
        "due_at",
        "is_completed",
        "is_reminder_sent",
        "created_at",
    ]
    list_filter = ["item_type", "priority", "is_completed", "is_reminder_sent"]
    search_fields = ["title", "description", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at"]
    raw_id_fields = ["user", "content_type"]
    list_per_page = 30
