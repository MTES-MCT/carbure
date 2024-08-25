from django.db import transaction

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.helpers import filter_lots, get_entity_lots_by_status
from core.models import CarbureLot, CarbureLotEvent, CarbureNotification, UserRights
from core.traceability import bulk_delete_traceability_nodes, bulk_update_traceability_nodes, get_traceability_nodes
from core.traceability.lot import LotNode
from transactions.api.admin.lots.update_many import group_lots_by_entity, serialize_node


class DeleteLotsError:
    NO_LOTS_FOUND = "NO_LOTS_FOUND"
    DELETION_FORBIDDEN = "DELETION_FORBIDDEN"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def lots_delete(request, entity):
    status = request.POST.get("status", None)
    dry_run = request.POST.get("dry_run") == "true"

    lots = get_entity_lots_by_status(entity, status)
    filtered_lots = filter_lots(lots, request.POST, entity)

    if filtered_lots.count() == 0:
        return ErrorResponse(400, DeleteLotsError.NO_LOTS_FOUND)

    # query the database for all the traceability nodes related to these lots
    nodes = get_traceability_nodes(filtered_lots)

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
        return ErrorResponse(400, DeleteLotsError.DELETION_FORBIDDEN, [lot.id for lot in delete_error_lots])

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

    return SuccessResponse({"deletions": deletions, "updates": updates})
