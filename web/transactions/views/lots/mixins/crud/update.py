from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from carbure.tasks import background_bulk_scoring
from core.carburetypes import CarbureStockErrors
from core.models import CarbureLotEvent, Entity, GenericError
from core.traceability import (
    LotNode,
    diff_to_metadata,
    get_traceability_nodes,
    serialize_integrity_errors,
)
from doublecount.helpers import get_lot_dc_agreement
from transactions.helpers import compute_lot_quantity
from transactions.sanity_checks.sanity_checks import (
    bulk_sanity_checks,
    get_prefetched_data,
)
from transactions.serializers.lot_serilizer import LotSerializer


class UpdateLotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    MISSING_LOT_ID = "MISSING_LOT_ID"
    LOT_NOT_FOUND = "LOT_NOT_FOUND"
    LOT_UPDATE_FAILED = "LOT_UPDATE_FAILED"
    FIELD_UPDATE_FORBIDDEN = "FIELD_UPDATE_FORBIDDEN"
    INTEGRITY_CHECKS_FAILED = "INTEGRITY_CHECKS_FAILED"


class UpdateMixin:
    @extend_schema(
        examples=[
            OpenApiExample(
                "Example of assign response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
        request=LotSerializer,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="update-lot",
        serializer_class=LotSerializer,
    )
    def update_lot(self, request, id=None):
        entity_id = int(self.request.query_params.get("entity_id"))

        serializer = LotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_lot = self.get_object()
        entity = get_object_or_404(Entity, id=entity_id)

        if not updated_lot:  # or updated_lot.added_by != entity:
            raise ValidationError({"message": UpdateLotError.LOT_NOT_FOUND})

        prefetched_data = get_prefetched_data(entity)

        # convert the form data to a dict that can be applied as lot update
        update_data, quantity_data = serializer.get_lot_data(serializer.validated_data, request.data)

        update = {
            **update_data,
        }

        if len(quantity_data) > 0:
            biofuel = update.get("biofuel") or updated_lot.biofuel
            quantity = compute_lot_quantity(biofuel, quantity_data)
            update = {**update_data, **quantity}

        dc_agreement = get_lot_dc_agreement(
            update.get("feedstock"),
            update.get("delivery_date"),
            update.get("carbure_production_site"),
        )

        if dc_agreement:
            update["production_site_double_counting_certificate"] = dc_agreement

        # query the database for all the traceability nodes related to these lots
        nodes = get_traceability_nodes([updated_lot])
        lot_node = nodes[0]
        # make sure updating this lot doesn't cause any volume problem if any parent stock exists
        stock_update, stock_error = enforce_stock_integrity(lot_node, update)
        if stock_update is not None:
            update.update(stock_update)
        try:
            # apply the update to the lot and check if the given entity can actually apply it
            lot_node.update(update, entity_id)
            lot_node.data.update_ghg()

            integrity_errors = lot_node.check_integrity(ignore_diff=True)
            if len(integrity_errors) > 0:
                errors = serialize_integrity_errors(integrity_errors)
                return Response(
                    {
                        "message": UpdateLotError.INTEGRITY_CHECKS_FAILED,
                        "errors": errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"message": UpdateLotError.FIELD_UPDATE_FORBIDDEN, "errors": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            lot_node.data.save()

            bulk_sanity_checks([lot_node.data], prefetched_data)
            background_bulk_scoring([lot_node.data], prefetched_data)

            if stock_error is not None:
                stock_error.save()

            if len(lot_node.diff) > 0:
                CarbureLotEvent.objects.create(
                    event_type=CarbureLotEvent.UPDATED,
                    lot=lot_node.data,
                    user=request.user,
                    metadata=diff_to_metadata(lot_node.diff),
                )

        return Response({"status": "success"})


# before applying an update, check that if the lot comes from a stock
# the stock has enough volume left to allow the update
def enforce_stock_integrity(lot_node: LotNode, update: dict):
    ancestor_stock_node = lot_node.get_closest(LotNode.STOCK)

    if ancestor_stock_node is None:
        return None, None

    ancestor_stock = ancestor_stock_node.data
    volume_before_update = lot_node.data.volume
    volume_change = round(update["volume"] - volume_before_update, 2)

    # if the volume is above the allowed limit, reset it and create an error to explain why
    if volume_change > 0 and ancestor_stock.remaining_volume < volume_change:
        biofuel = update.get("biofuel") or lot_node.data.biofuel
        reset_quantity = compute_lot_quantity(biofuel, {"volume": volume_before_update})
        error = GenericError(
            lot=lot_node.data,
            field="quantity",
            error=CarbureStockErrors.NOT_ENOUGH_VOLUME_LEFT,
            display_to_creator=True,
        )
        return reset_quantity, error

    # otherwise, update the parent stock volume to match the new reality
    ancestor_stock.remaining_volume = round(ancestor_stock.remaining_volume - volume_change, 2)
    ancestor_stock.remaining_weight = ancestor_stock.get_weight()
    ancestor_stock.remaining_lhv_amount = ancestor_stock.get_lhv_amount()
    ancestor_stock.save()

    return None, None
