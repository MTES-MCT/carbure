from django import forms
from django.db import transaction
from core.carburetypes import CarbureError
from core.decorators import check_admin_rights
from core.common import SuccessResponse, ErrorResponse

from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureLotComment,
    CarbureNotification,
)

from core.traceability import (
    LotNode,
    get_traceability_nodes,
    bulk_update_traceability_nodes,
    bulk_delete_traceability_nodes,
)

from .update_many import group_lots_by_entity, serialize_node


@check_admin_rights()
def delete_many(request):
    form = DeleteManyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    comment = form.cleaned_data["comment"]
    dry_run = form.cleaned_data["dry_run"]
    lots = form.cleaned_data["lots_ids"]

    # query the database for all the traceability nodes related to these lots
    nodes = get_traceability_nodes(lots)

    deleted_nodes = []
    updated_nodes = []

    for node in nodes:
        # recursively remove the node and update its parents
        deleted, updated = node.delete()

        deleted_nodes += deleted
        updated_nodes += updated

    # prepare lot events and comments
    update_events = []
    update_comments = []

    for node in deleted_nodes:
        if not isinstance(node, LotNode):
            continue

        # save a lot event with the current modification
        update_events.append(
            CarbureLotEvent(
                event_type=CarbureLotEvent.DELETED_BY_ADMIN,
                lot=node.data,
                user=request.user,
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

        delete_notifications.append(
            CarbureNotification(
                dest_id=entity_id,
                type=CarbureNotification.LOTS_DELETED_BY_ADMIN,
                acked=False,
                email_sent=False,
                meta={"deleted": len(deleted), "updated": len(updated), "comment": comment},
            )
        )

    # save everything in the database in one single transaction
    if not dry_run:
        with transaction.atomic():
            bulk_update_traceability_nodes(updated_nodes)
            bulk_delete_traceability_nodes(deleted_nodes)
            CarbureLotComment.objects.bulk_create(update_comments)
            CarbureLotEvent.objects.bulk_create(update_events)
            CarbureNotification.objects.bulk_create(delete_notifications)

    # prepare the response data
    deletions = [serialize_node(node) for node in deleted_nodes]
    updates = [serialize_node(node) for node in updated_nodes]

    return SuccessResponse({"deletions": deletions, "updates": updates})


class DeleteManyForm(forms.Form):
    # choices
    LOTS = CarbureLot.objects.all()

    # config fields
    entity_id = forms.IntegerField()
    lots_ids = forms.ModelMultipleChoiceField(queryset=LOTS)
    comment = forms.CharField()
    dry_run = forms.BooleanField(required=False)
