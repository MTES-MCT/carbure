from django import forms
from django.db import transaction

from carbure.tasks import background_bulk_scoring
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import (
    CarbureLotComment,
    CarbureLotEvent,
    CarbureNotification,
    GenericError,
)
from core.serializers import GenericErrorSerializer
from core.traceability import (
    LotNode,
    bulk_update_traceability_nodes,
    diff_to_metadata,
    get_traceability_nodes,
    serialize_integrity_errors,
)
from transactions.forms import LotForm
from transactions.helpers import compute_lot_quantity
from transactions.sanity_checks import bulk_sanity_checks, get_prefetched_data


class UpdateManyError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    INTEGRITY_CHECKS_FAILED = "INTEGRITY_CHECKS_FAILED"
    SANITY_CHECKS_FAILED = "SANITY_CHECKS_FAILED"
    UPDATE_FAILED = "UPDATE_FAILED"


class UpdateManyForm(forms.Form):
    entity_id = forms.IntegerField()
    lots_ids = forms.ModelMultipleChoiceField(queryset=LotForm.LOTS)
    comment = forms.CharField()
    dry_run = forms.BooleanField(required=False)


@check_admin_rights()
def update_many(request):
    params_form = UpdateManyForm(request.POST)
    lot_form = LotForm(request.POST)

    if not params_form.is_valid() or not lot_form.is_valid():
        return ErrorResponse(400, UpdateManyError.MALFORMED_PARAMS, {**params_form.errors, **lot_form.errors})

    entity_id = params_form.cleaned_data["entity_id"]
    comment = params_form.cleaned_data["comment"]
    dry_run = params_form.cleaned_data["dry_run"]
    updated = params_form.cleaned_data["lots_ids"]

    prefetched_data = get_prefetched_data()

    # query the database for all the traceability nodes related to these lots
    nodes = get_traceability_nodes(updated)

    # convert the form data to a dict that can be applied as lot update
    update_data, quantity_data = lot_form.get_lot_data(ignore_empty=True)

    # prepare a list to hold all the nodes modified by this update
    updated_nodes = []

    # list integrity errors per selected lot
    integrity_errors = {}

    for node in nodes:
        # compute the update content based on the current lot
        update = {**update_data}
        biofuel = update.get("biofuel") or node.data.biofuel
        if len(quantity_data) > 0:
            quantity = compute_lot_quantity(biofuel, quantity_data)
            update = {**update, **quantity}

        # apply the update to the lot
        node.update(update)

        # check if the new values of the node can be applied in the current state
        node_errors = node.check_integrity(ignore_diff=True)
        if len(node_errors) > 0:
            integrity_errors[node.data.id] = node_errors

        # if the node changed, recursively apply the update to related nodes
        if len(node.diff) > 0:
            updated_nodes += node.propagate(changed_only=True)

    if len(integrity_errors) > 0:
        errors = {lot_id: serialize_integrity_errors(errors) for lot_id, errors in integrity_errors.items()}
        return ErrorResponse(400, UpdateManyError.INTEGRITY_CHECKS_FAILED, {"errors": errors})

    # prepare lot events and comments
    updated_lots = []
    update_events = []
    update_comments = []

    for node in updated_nodes:
        if not isinstance(node, LotNode) or len(node.diff) == 0:
            continue

        # list all the affected CarbureLots
        updated_lots.append(node.data)

        # recompute the GHG values in case something changed
        node.data.update_ghg()

        # save a lot event with the current modification
        update_events.append(
            CarbureLotEvent(
                event_type=CarbureLotEvent.UPDATED_BY_ADMIN,
                lot=node.data,
                user=request.user,
                metadata=diff_to_metadata(node.diff),
            )
        )

        # add a comment to the lot
        update_comments.append(
            CarbureLotComment(
                entity_id=entity_id,
                user=request.user,
                lot=node.data,
                comment=comment,
                comment_type=CarbureLotComment.ADMIN,
                is_visible_by_admin=True,
                is_visible_by_auditor=True,
            )
        )

    # run sanity checks in memory so we don't modify the current errors
    sanity_check_errors = bulk_sanity_checks(updated_lots, prefetched_data, dry_run=True)
    blocking_errors = [error for error in sanity_check_errors if error.is_blocking]

    # do not modify the database if there are any blocking errors in the modified lots
    if len(blocking_errors) > 0:
        errors_by_lot = group_errors_by_lot(blocking_errors)
        return ErrorResponse(400, UpdateManyError.SANITY_CHECKS_FAILED, {"errors": errors_by_lot})

    # prepare notifications to be sent to relevant entities
    update_notifications = []

    lots_by_entity = group_lots_by_entity(updated_lots)

    for entity_id, updated in lots_by_entity.items():
        update_notifications.append(
            CarbureNotification(
                dest_id=entity_id,
                type=CarbureNotification.LOTS_UPDATED_BY_ADMIN,
                acked=False,
                email_sent=False,
                meta={"updated": len(updated), "comment": comment},
            )
        )

    # save everything in the database in one single transaction
    if not dry_run:
        background_bulk_scoring(updated_lots, prefetched_data)

        with transaction.atomic():
            bulk_update_traceability_nodes(updated_nodes)
            CarbureLotComment.objects.bulk_create(update_comments)
            CarbureLotEvent.objects.bulk_create(update_events)
            CarbureNotification.objects.bulk_create(update_notifications)
            GenericError.objects.filter(lot__in=updated_lots).delete()
            GenericError.objects.bulk_create(sanity_check_errors)

    # prepare the response data
    updates = [serialize_node(node) for node in updated_nodes]
    errors_by_lot = group_errors_by_lot(sanity_check_errors)

    return SuccessResponse({"updates": updates, "errors": errors_by_lot})


def serialize_node(node):
    return {"node": node.serialize(), "diff": diff_to_metadata(node.diff)}


# group a list of GenericError by the id of their related CarbureLot
def group_errors_by_lot(errors) -> dict[int, list[dict]]:
    errors_by_lot = {}
    for error in errors:
        if error.lot_id not in errors_by_lot:
            errors_by_lot[error.lot_id] = []
        errors_by_lot[error.lot_id].append(error)
    for lot_id in errors_by_lot:
        errors_by_lot[lot_id] = GenericErrorSerializer(errors_by_lot[lot_id], many=True).data
    return errors_by_lot


# group lots by their owners and clients
def group_lots_by_entity(lots):
    lots_by_entity = {}

    for lot in lots:
        added_by = lot.added_by_id
        client = lot.carbure_client_id

        if added_by not in lots_by_entity:
            lots_by_entity[added_by] = []

        # the lot is linked to its owner entity
        lots_by_entity[added_by].append(lot)

        # skip the rest if there's not known client or the client is the owner
        if not client or added_by == client:
            continue

        if client not in lots_by_entity:
            lots_by_entity[client] = []

        # and the lot is also linked to its client entity
        lots_by_entity[client].append(lot)

    return lots_by_entity
