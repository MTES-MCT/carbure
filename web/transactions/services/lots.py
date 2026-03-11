from django.db import transaction

from carbure.tasks import background_bulk_scoring
from core.carburetypes import CarbureStockErrors
from core.models import CarbureLotEvent, GenericError
from core.serializers import CarbureLotPublicSerializer
from core.traceability import LotNode, diff_to_metadata, get_traceability_nodes, serialize_integrity_errors
from doublecount.helpers import get_lot_dc_agreement
from transactions.helpers import bulk_insert_lots, compute_lot_quantity, construct_carbure_lot
from transactions.sanity_checks.helpers import get_prefetched_data
from transactions.sanity_checks.sanity_checks import bulk_sanity_checks


class LotCreationFailure(RuntimeError):
    pass


class LotUpdateFailure(RuntimeError):
    INTEGRITY_CHECKS_FAILED = "INTEGRITY_CHECKS_FAILED"

    def __init__(self, message, data):
        self.message = message
        self.data = data


def create_lot(user, entity, source, lot_data):
    d = get_prefetched_data(entity)
    lot, errors = construct_carbure_lot(d, entity, lot_data)

    if not lot:
        raise LotCreationFailure()

    with transaction.atomic():
        lots_created = bulk_insert_lots(entity, [lot], [errors], d)

        if len(lots_created) == 0:
            raise LotCreationFailure()

        background_bulk_scoring(lots_created)

        CarbureLotEvent.objects.create(
            event_type=CarbureLotEvent.CREATED,
            lot_id=lots_created[0].id,
            user=user,
            metadata={"source": source},
            entity=entity,
        )

    return CarbureLotPublicSerializer(lots_created[0]).data


def do_update_lot(user, entity, updated_lot, update):
    prefetched_data = get_prefetched_data(entity)

    dc_agreement = get_lot_dc_agreement(
        update.get("feedstock"),
        update.get("delivery_date"),
        update.get("carbure_production_site"),
    )

    if dc_agreement:
        update["production_site_double_counting_certificate"] = dc_agreement

    nodes = get_traceability_nodes([updated_lot])
    lot_node = nodes[0]
    stock_update, stock_error = enforce_stock_integrity(lot_node, update)
    if stock_update is not None:
        update.update(stock_update)

    lot_node.update(update, entity.id)
    lot_node.data.update_ghg()

    integrity_errors = lot_node.check_integrity(ignore_diff=True)
    if len(integrity_errors) > 0:
        errors = serialize_integrity_errors(integrity_errors)
        raise LotUpdateFailure(LotUpdateFailure.INTEGRITY_CHECKS_FAILED, {"errors": errors})

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
                user=user,
                metadata=diff_to_metadata(lot_node.diff),
                entity=entity,
            )


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
