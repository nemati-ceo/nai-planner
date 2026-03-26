from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from nai_planner.contrib.drf.filters import PlannerItemFilter
from nai_planner.contrib.drf.serializers import (
    PlannerItemListSerializer,
    PlannerItemSerializer,
)
from nai_planner.models import PlannerItem


class PlannerItemViewSet(viewsets.ModelViewSet):
    """
    CRUD for planner items (tasks, events, reminders).

    Filter by type:  ?item_type=task
    Filter by date:  ?due_after=2025-01-01&due_before=2025-12-31
    Filter by done:  ?is_completed=true
    """

    permission_classes = [permissions.IsAuthenticated]
    filterset_class = PlannerItemFilter
    lookup_field = "uuid"

    def get_queryset(self):
        return PlannerItem.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PlannerItemListSerializer
        return PlannerItemSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def complete(self, request, uuid=None):
        """Mark a task/reminder as completed."""
        item = self.get_object()
        item.is_completed = True
        item.save(update_fields=["is_completed", "updated_at"])
        return Response(
            PlannerItemSerializer(item).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def restore(self, request, uuid=None):
        """Restore a soft-deleted item."""
        item = PlannerItem.all_objects.filter(
            uuid=uuid,
            user=request.user,
            deleted_at__isnull=False,
        ).first()
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        item.restore()
        return Response(
            PlannerItemSerializer(item).data,
            status=status.HTTP_200_OK,
        )
