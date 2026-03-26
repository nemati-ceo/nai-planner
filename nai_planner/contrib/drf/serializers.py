from rest_framework import serializers

from nai_planner.models import PlannerItem


class PlannerItemSerializer(serializers.ModelSerializer):
    linked_model = serializers.CharField(
        write_only=True,
        required=False,
        help_text="app_label.ModelName (e.g. 'notes.Note')",
    )
    linked_object_id = serializers.IntegerField(
        write_only=True,
        required=False,
    )

    class Meta:
        model = PlannerItem
        fields = [
            "uuid",
            "item_type",
            "title",
            "description",
            "priority",
            "due_at",
            "end_at",
            "remind_at",
            "is_all_day",
            "recurrence",
            "is_completed",
            "is_reminder_sent",
            "is_overdue",
            "linked_model",
            "linked_object_id",
            "content_type",
            "object_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "is_reminder_sent",
            "is_overdue",
            "content_type",
            "object_id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        linked_model = attrs.pop("linked_model", None)
        linked_object_id = attrs.pop("linked_object_id", None)

        if linked_model and linked_object_id:
            from django.contrib.contenttypes.models import ContentType

            try:
                app_label, model_name = linked_model.split(".")
                ct = ContentType.objects.get(
                    app_label=app_label.lower(),
                    model=model_name.lower(),
                )
            except (ValueError, ContentType.DoesNotExist):
                raise serializers.ValidationError(
                    {"linked_model": f"Invalid model: {linked_model}"}
                )

            # Verify the target object exists
            model_class = ct.model_class()
            if not model_class.objects.filter(pk=linked_object_id).exists():
                raise serializers.ValidationError(
                    {"linked_object_id": "Target object not found."}
                )

            attrs["content_type"] = ct
            attrs["object_id"] = linked_object_id

        elif linked_model or linked_object_id:
            raise serializers.ValidationError(
                "Both linked_model and linked_object_id are required together."
            )

        # Validate end_at only for events
        if attrs.get("end_at") and attrs.get("item_type") != PlannerItem.ItemType.EVENT:
            raise serializers.ValidationError(
                {"end_at": "end_at is only valid for calendar events."}
            )

        return attrs


class PlannerItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""

    class Meta:
        model = PlannerItem
        fields = [
            "uuid",
            "item_type",
            "title",
            "priority",
            "due_at",
            "is_all_day",
            "is_completed",
            "is_overdue",
            "created_at",
        ]
        read_only_fields = fields
