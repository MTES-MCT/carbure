from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent, CarbureNotification, Entity
from core.traceability import (
    bulk_delete_traceability_nodes,
    bulk_update_traceability_nodes,
    get_traceability_nodes,
)
from core.traceability.lot import LotNode

from .update_many import group_lots_by_entity, serialize_node


class DeleteLotsError:
    NO_LOTS_FOUND = "NO_LOTS_FOUND"
    DELETION_FORBIDDEN = "DELETION_FORBIDDEN"


class DeleteLotsSerializer(serializers.Serializer):
    dry_run = serializers.BooleanField(default=False)
    selection = serializers.PrimaryKeyRelatedField(queryset=CarbureLot.objects.all(), many=True)


class DeleteLotsNodeDiffSerializer(serializers.Serializer):
    node = serializers.DictField()
    diff = serializers.DictField()


class DeleteLotsResponseSerializer(serializers.Serializer):
    deletions = serializers.ListField(child=DeleteLotsNodeDiffSerializer())
    updates = serializers.ListField(child=DeleteLotsNodeDiffSerializer())


class DeleteLotsMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        request=DeleteLotsSerializer,
        responses=DeleteLotsResponseSerializer,
    )
    @action(methods=["post"], detail=False, serializer_class=DeleteLotsSerializer)
    def delete(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)

        serializer = DeleteLotsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dry_run = serializer.validated_data["dry_run"]
        lots = serializer.validated_data["selection"]

        if len(lots) == 0:
            raise ValidationError({"message": DeleteLotsError.NO_LOTS_FOUND})

        # query the database for all the traceability nodes related to these lots
        nodes = get_traceability_nodes(lots)
        deleted_nodes = []
        updated_nodes = []

        delete_error_lots = []

        for node in nodes:
            try:
                # remove the node and update its parents
                deleted, updated = node.delete(entity.id)
                deleted_nodes += deleted
                updated_nodes += updated
            except Exception:
                delete_error_lots.append(node.data)

        if len(delete_error_lots) > 0:
            raise ValidationError(
                {
                    "message": DeleteLotsError.DELETION_FORBIDDEN,
                    "lots": [lot.id for lot in delete_error_lots],
                }
            )

        # prepare lot event list
        update_events = []

        for node in deleted_nodes:
            # only create events for lots that are also not drafts
            if not isinstance(node, LotNode) or node.data.lot_status == CarbureLot.DRAFT:
                continue

            # save a lot event with the current modification
            update_events.append(
                CarbureLotEvent(
                    event_type=CarbureLotEvent.DELETED,
                    lot=node.data,
                    user=request.user,
                )
            )

        # prepare notifications to be sent to relevant entities
        delete_notifications = []

        deleted_lots = [node.data for node in deleted_nodes if isinstance(node, LotNode)]
        updated_lots = [node.data for node in updated_nodes if isinstance(node, LotNode)]

        deleted_by_entity = group_lots_by_entity(deleted_lots)
        updated_by_entity = group_lots_by_entity(updated_lots)

        # merge the two dicts to get all the entity_ids that should be notified
        entity_ids = list({**deleted_by_entity, **updated_by_entity})

        for entity_id in entity_ids:
            deleted = deleted_by_entity.get(entity_id, [])
            updated = updated_by_entity.get(entity_id, [])

        # save everything in the database in one single transaction
        if not dry_run:
            with transaction.atomic():
                bulk_update_traceability_nodes(updated_nodes)
                bulk_delete_traceability_nodes(deleted_nodes)
                CarbureLotEvent.objects.bulk_create(update_events)
                CarbureNotification.objects.bulk_create(delete_notifications)

        # prepare the response data
        deletions = [serialize_node(node) for node in deleted_nodes]
        updates = [serialize_node(node) for node in updated_nodes]

        return Response({"deletions": deletions, "updates": updates})
