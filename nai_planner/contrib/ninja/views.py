from uuid import UUID

from django.shortcuts import get_object_or_404
from ninja import Query, Router

from nai_planner.contrib.ninja.schemas import (
    PlannerItemCreateSchema,
    PlannerItemListSchema,
    PlannerItemOutSchema,
    PlannerItemUpdateSchema,
)
from nai_planner.models import PlannerItem

router = Router(tags=["planner"])


def _resolve_generic_fk(data: dict) -> dict:
    """Resolve linked_model + linked_object_id into content_type + object_id."""
    linked_model = data.pop("linked_model", None)
    linked_object_id = data.pop("linked_object_id", None)

    if linked_model and linked_object_id:
        from django.contrib.contenttypes.models import ContentType

        app_label, model_name = linked_model.split(".")
        ct = ContentType.objects.get(
            app_label=app_label.lower(),
            model=model_name.lower(),
        )
        model_class = ct.model_class()
        if not model_class.objects.filter(pk=linked_object_id).exists():
            raise ValueError(f"Target object {linked_model}:{linked_object_id} not found.")
        data["content_type"] = ct
        data["object_id"] = linked_object_id

    return data


@router.get("/", response=list[PlannerItemListSchema])
def list_items(
    request,
    item_type: str | None = Query(None),
    priority: str | None = Query(None),
    is_completed: bool | None = Query(None),
):
    qs = PlannerItem.objects.filter(user=request.user)
    if item_type:
        qs = qs.filter(item_type=item_type)
    if priority:
        qs = qs.filter(priority=priority)
    if is_completed is not None:
        qs = qs.filter(is_completed=is_completed)
    return qs


@router.post("/", response={201: PlannerItemOutSchema})
def create_item(request, payload: PlannerItemCreateSchema):
    data = payload.dict()
    data = _resolve_generic_fk(data)
    item = PlannerItem.objects.create(user=request.user, **data)
    return 201, item


@router.get("/{item_uuid}/", response=PlannerItemOutSchema)
def get_item(request, item_uuid: UUID):
    return get_object_or_404(PlannerItem, uuid=item_uuid, user=request.user)


@router.patch("/{item_uuid}/", response=PlannerItemOutSchema)
def update_item(request, item_uuid: UUID, payload: PlannerItemUpdateSchema):
    item = get_object_or_404(PlannerItem, uuid=item_uuid, user=request.user)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(item, field, value)
    item.save()
    return item


@router.delete("/{item_uuid}/", response={204: None})
def delete_item(request, item_uuid: UUID):
    item = get_object_or_404(PlannerItem, uuid=item_uuid, user=request.user)
    item.soft_delete()
    return 204, None


@router.post("/{item_uuid}/complete/", response=PlannerItemOutSchema)
def complete_item(request, item_uuid: UUID):
    item = get_object_or_404(PlannerItem, uuid=item_uuid, user=request.user)
    item.is_completed = True
    item.save(update_fields=["is_completed", "updated_at"])
    return item


@router.post("/{item_uuid}/restore/", response=PlannerItemOutSchema)
def restore_item(request, item_uuid: UUID):
    item = PlannerItem.all_objects.filter(
        uuid=item_uuid,
        user=request.user,
        deleted_at__isnull=False,
    ).first()
    if not item:
        from ninja.errors import HttpError
        raise HttpError(404, "Item not found or not deleted.")
    item.restore()
    return item
