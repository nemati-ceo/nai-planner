from django_filters import rest_framework as filters

from nai_planner.models import PlannerItem


class PlannerItemFilter(filters.FilterSet):
    item_type = filters.ChoiceFilter(choices=PlannerItem.ItemType.choices)
    priority = filters.ChoiceFilter(choices=PlannerItem.Priority.choices)
    is_completed = filters.BooleanFilter()
    due_after = filters.DateTimeFilter(field_name="due_at", lookup_expr="gte")
    due_before = filters.DateTimeFilter(field_name="due_at", lookup_expr="lte")

    class Meta:
        model = PlannerItem
        fields = ["item_type", "priority", "is_completed"]
