from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent, GenericError
from core.notifications import notify_correction_done
from core.traceability import Node, bulk_update_traceability_nodes, diff_to_metadata, get_traceability_nodes


class SubmitFixError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    FROZEN_LOT = "FROZEN_LOT"
    UNAUTHORIZED_ENTITY = "UNAUTHORIZED_ENTITY"
    BLOCKING_SANITY_CHECK = "BLOCKING_SANITY_CHECK"


class SubmitFixSerializer(serializers.Serializer):
    # config fields
    lot_ids = serializers.PrimaryKeyRelatedField(queryset=CarbureLot.objects.all(), many=True)


class SubmitFixMixin:
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
        request=SubmitFixSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="submit-fix")
    def submit_fix(self, request, *args, **kwargs):
        entity_id = int(self.request.query_params.get("entity_id"))

        serializer = SubmitFixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lot_instances = serializer.validated_data["lot_ids"]

        lot_ids = [lot.id for lot in lot_instances]

        lots = CarbureLot.objects.filter(id__in=lot_ids)

        submit_fix_events = []

        for lot in lots:
            if lot.lot_status == CarbureLot.FROZEN:
                raise ValidationError({"message": SubmitFixError.FROZEN_LOT})

            if lot.added_by_id != entity_id:
                raise ValidationError({"message": SubmitFixError.UNAUTHORIZED_ENTITY})

            if GenericError.objects.filter(lot=lot, is_blocking=True).count() > 0:
                raise ValidationError({"message": SubmitFixError.BLOCKING_SANITY_CHECK})

            event = CarbureLotEvent(event_type=CarbureLotEvent.MARKED_AS_FIXED, lot=lot, user=request.user)
            submit_fix_events.append(event)

        rejected_lots = lots.filter(lot_status=CarbureLot.REJECTED)
        fix_lots = lots.filter(correction_status=CarbureLot.IN_CORRECTION)
        own_lots = lots.filter(added_by_id=entity_id).filter(Q(carbure_client_id=entity_id) | Q(carbure_client_id=None))

        # query the database for all the traceability nodes related to these lots
        nodes = get_traceability_nodes(fix_lots)

        updated_nodes = []
        for node in nodes:
            # propagate the corrections to any other connected model
            updated_nodes += node.propagate()

        # prepare a list of update events so we know how lots were updated after propagation
        updated_lots = []
        update_events = []
        for node in updated_nodes:
            if node.type == Node.LOT:
                updated_lots.append(node)

                if len(node.diff) > 0:
                    update_events.append(
                        CarbureLotEvent(
                            event_type=CarbureLotEvent.UPDATED,
                            lot=node.data,
                            user=request.user,
                            metadata=diff_to_metadata(node.diff),
                        )
                    )

        with transaction.atomic():
            rejected_lots.update(lot_status=CarbureLot.PENDING, correction_status=CarbureLot.NO_PROBLEMO)
            fix_lots.update(correction_status=CarbureLot.FIXED)
            own_lots.update(correction_status=CarbureLot.NO_PROBLEMO)

            bulk_update_traceability_nodes(updated_nodes)

            CarbureLotEvent.objects.bulk_create(submit_fix_events)
            CarbureLotEvent.objects.bulk_create(update_events)
            notify_correction_done(lots.exclude(carbure_client_id=entity_id))

        return Response({})
