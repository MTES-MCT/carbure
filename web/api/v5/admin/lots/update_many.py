from django import forms
from django.db import transaction
from core.decorators import check_admin_rights
from core.common import SuccessResponse, ErrorResponse
from core.serializers import GenericErrorSerializer
from core.carburetypes import CarbureUnit
from producers.models import ProductionSite
from api.v4.lots import compute_lot_quantity
from api.v4.sanity_checks import bulk_sanity_checks, get_prefetched_data
from carbure.tasks import background_bulk_scoring

from core.models import (
    CarbureLot,
    Entity,
    Biocarburant,
    MatierePremiere,
    Depot,
    Pays,
    CarbureLotEvent,
    CarbureLotComment,
    GenericError,
    CarbureNotification,
)

from core.traceability import (
    LotNode,
    get_traceability_nodes,
    bulk_update_traceability_nodes,
)


class UpdateManyError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SANITY_CHECKS_FAILED = "SANITY_CHECKS_FAILED"
    UPDATE_FAILED = "UPDATE_FAILED"


@check_admin_rights()
def update_many(request):
    form = UpdateManyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, UpdateManyError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    comment = form.cleaned_data["comment"]
    dry_run = form.cleaned_data["dry_run"]
    updated = form.cleaned_data["lots_ids"]

    prefetched_data = get_prefetched_data()

    # query the database for all the traceability nodes related to these lots
    nodes = get_traceability_nodes(updated)

    # convert the form data to a dict that can be applied as lot update
    update_data, quantity_data = get_update_data(form.cleaned_data)

    # prepare a list to hold all the nodes modified by this update
    updated_nodes = []

    for node in nodes:
        # compute the update content based on the current lot
        update = {**update_data}
        if len(quantity_data) > 0:
            quantity = compute_lot_quantity(node.data, quantity_data)
            update = {**update, **quantity}

        # apply the update to the lot
        node.update(update)

        # if the node changed, recursively apply the update to related nodes
        if len(node.diff) > 0:
            updated_nodes += node.propagate(changed_only=True)

    # prepare lot events and comments
    updated_lots = []
    update_events = []
    update_comments = []

    for node in updated_nodes:
        if not isinstance(node, LotNode) or len(node.diff) == 0:
            continue

        # list all the affected CarbureLots
        updated_lots.append(node.data)

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
    sanity_check_errors, _ = bulk_sanity_checks(updated_lots, prefetched_data, dry_run=True)
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


class UpdateManyForm(forms.Form):
    # choices
    UNITS = ((CarbureUnit.LITER, "l"), (CarbureUnit.KILOGRAM, "kg"), (CarbureUnit.LHV, "pci"))
    LOTS = CarbureLot.objects.all()
    ENTITIES = Entity.objects.all()
    PRODUCERS = Entity.objects.filter(entity_type=Entity.PRODUCER)
    BIOFUELS = Biocarburant.objects.all()
    FEEDSTOCKS = MatierePremiere.objects.all()
    COUNTRIES = Pays.objects.all()
    PRODUCTION_SITES = ProductionSite.objects.all()
    DEPOTS = Depot.objects.all()

    # config fields
    entity_id = forms.IntegerField()
    lots_ids = forms.ModelMultipleChoiceField(queryset=LOTS)
    comment = forms.CharField()
    dry_run = forms.BooleanField(required=False)

    # lot fields
    transport_document_type = forms.CharField(required=False)
    transport_document_reference = forms.CharField(required=False)

    quantity = forms.FloatField(min_value=0, required=False)
    unit = forms.ChoiceField(choices=UNITS, required=False)

    biofuel_code = forms.ModelChoiceField(queryset=BIOFUELS, to_field_name="code", required=False)
    feedstock_code = forms.ModelChoiceField(queryset=FEEDSTOCKS, to_field_name="code", required=False)
    country_code = forms.ModelChoiceField(queryset=COUNTRIES, to_field_name="code_pays", required=False)

    free_field = forms.CharField(required=False)

    eec = forms.FloatField(required=False)
    el = forms.FloatField(required=False)
    ep = forms.FloatField(required=False)
    etd = forms.FloatField(required=False)
    eu = forms.FloatField(required=False)
    esca = forms.FloatField(required=False)
    eccs = forms.FloatField(required=False)
    eccr = forms.FloatField(required=False)
    eee = forms.FloatField(required=False)

    carbure_producer_id = forms.ModelChoiceField(queryset=PRODUCERS, required=False)
    unknown_producer = forms.CharField(required=False)
    carbure_production_site = forms.ModelChoiceField(queryset=PRODUCTION_SITES, required=False)
    unknown_production_site = forms.CharField(required=False)
    production_site_certificate = forms.CharField(required=False)
    production_site_certificate_type = forms.CharField(required=False)
    production_country_code = forms.CharField(required=False)
    production_site_commissioning_date = forms.DateField(required=False)
    production_site_double_counting_certificate = forms.CharField(required=False)

    carbure_supplier_id = forms.ModelChoiceField(queryset=ENTITIES, required=False)
    unknown_supplier = forms.CharField(required=False)
    supplier_certificate = forms.CharField(required=False)
    supplier_certificate_type = forms.CharField(required=False)
    vendor_certificate = forms.CharField(required=False)
    vendor_certificate_type = forms.CharField(required=False)
    delivery_type = forms.CharField(required=False)
    delivery_date = forms.DateField(required=False)
    carbure_client_id = forms.ModelChoiceField(queryset=ENTITIES, required=False)
    unknown_client = forms.CharField(required=False)
    carbure_delivery_site_depot_id = forms.ModelChoiceField(queryset=DEPOTS, to_field_name="depot_id", required=False)
    unknown_delivery_site = forms.CharField(required=False)
    delivery_site_country_code = forms.ModelChoiceField(queryset=COUNTRIES, to_field_name="code_pays", required=False)


# grab only the values that are defined on the form data
# and transform them so they can be applied directly to a CarbureLot
def get_update_data(form_data):
    update_data = {}
    quantity_data = {}

    for field in form_data:
        if field in ("lots_ids", "comment", "entity_id", "dry_run"):
            continue

        if form_data[field] in ("", None):
            continue

        lot_field = FORM_TO_LOT_FIELD.get(field, field)

        if field in ("quantity", "unit", "volume", "weight", "lhv_amount"):
            quantity_data[field] = form_data[field]
        elif field in FORM_TO_LOT_FIELD:
            update_data[lot_field] = form_data[field].id
        else:
            update_data[field] = form_data[field]

    return update_data, quantity_data


def serialize_node(node):
    return {"node": node.serialize(), "diff": node.diff}


# transform the node diff into an dict that can be stored as the metadata of an update CarbureLotEvent
def diff_to_metadata(diff: dict):
    metadata = {"added": [], "removed": [], "changed": []}
    for field, (new_value, old_value) in diff.items():
        metadata["changed"].append([field, old_value, new_value])
    return metadata


# group a list of GenericError by the id of their related CarbureLot
def group_errors_by_lot(errors) -> dict[int, list[dict]]:
    errors_by_lot = {}
    for error in errors:
        if error.lot_id not in errors_by_lot:
            errors_by_lot[error.lot_id] = []
        errors_by_lot[error.lot_id].append(error)
    for lot_id, errors in errors_by_lot.items():
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


# map form fields to CarbureLot model fields
FORM_TO_LOT_FIELD = {
    "biofuel_code": "biofuel_id",
    "feedstock_code": "feedstock_id",
    "country_code": "country_of_origin_id",
    "carbure_producer_id": "carbure_producer_id",
    "production_country_code": "production_country_id",
    "carbure_supplier_id": "carbure_supplier_id",
    "carbure_client_id": "carbure_client_id",
    "carbure_delivery_site_depot_id": "carbure_delivery_site_id",
    "delivery_site_country_code": "delivery_site_country_id",
}
