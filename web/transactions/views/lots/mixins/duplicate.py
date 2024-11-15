from django.db.models.fields import NOT_PROVIDED
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent, Entity
from transactions.sanity_checks import bulk_sanity_checks, bulk_scoring, get_prefetched_data


class DuplicateMixin:
    @extend_schema(
        examples=[
            OpenApiExample(
                "Example of assign response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["get"], detail=True)
    def duplicate(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        lot = self.get_object()

        if lot.added_by_id != int(entity_id):
            raise PermissionDenied({"message": "User not allowed"})

        lot.pk = None
        lot.parent_stock = None
        lot.parent_lot = None
        lot_fields_to_remove = [
            "carbure_id",
            "correction_status",
            "lot_status",
            "delivery_status",
            "declared_by_supplier",
            "declared_by_client",
            "highlighted_by_admin",
            "highlighted_by_auditor",
        ]
        lot_meta_fields = {f.name: f for f in CarbureLot._meta.get_fields()}
        for f in lot_fields_to_remove:
            if f in lot_meta_fields:
                meta_field = lot_meta_fields[f]
                if meta_field.default != NOT_PROVIDED:
                    setattr(lot, f, meta_field.default)
                else:
                    setattr(lot, f, "")
        lot.save()

        e = CarbureLotEvent()
        e.event_type = CarbureLotEvent.CREATED
        e.lot_id = lot.pk
        e.user = request.user
        e.metadata = {"source": "MANUAL"}
        e.save()
        data = get_prefetched_data(entity)
        bulk_sanity_checks([lot], data)
        bulk_scoring([lot], data)
        return Response({"status": "success"})
