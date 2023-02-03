from django import forms
from django.db import transaction
from core.carburetypes import CarbureUnit
from core.decorators import check_admin_rights
from core.serializers import GenericErrorSerializer
from core.traceability_tree import LotNode, StockNode, StockTransformNode, TicketSourceNode, TicketNode
from core.traceability_query import get_lots_family_trees
from producers.models import ProductionSite
from core.common import SuccessResponse, ErrorResponse
from api.v4.sanity_checks import bulk_sanity_checks
from api.v4.lots import compute_lot_quantity


from core.models import (
    CarbureLot,
    Entity,
    Biocarburant,
    MatierePremiere,
    Depot,
    Pays,
    GenericError,
    CarbureLotEvent,
    CarbureLotComment,
)


class UpdateManyError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SANITY_CHECKS_NOT_PASSED = "SANITY_CHECKS_NOT_PASSED"
    SOME_LOTS_HAVE_PARENTS = "SOME_LOTS_HAVE_PARENTS"


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


@check_admin_rights()
def update_many(request):
    form = UpdateManyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, UpdateManyError.MALFORMED_PARAMS, form.errors)

    entity_id = form.cleaned_data["entity_id"]
    comment = form.cleaned_data["comment"]
    dry_run = form.cleaned_data["dry_run"]
    lots = form.cleaned_data["lots_ids"]

    update_data, quantity_data, update_fields = get_update_data(form.cleaned_data)

    updated_nodes = []
    updated_lots = []
    update_events = []
    update_comments = []

    nodes = get_lots_family_trees(lots)

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

    # dedupe the nodes so we don't create duplicates
    updated_nodes = list(set(updated_nodes))

    updated_lots = []
    updated_stocks = []
    updated_stock_transforms = []
    updated_ticket_sources = []
    updated_tickets = []

    # get the list of lots modified by this update
    for node in updated_nodes:
        if isinstance(node, LotNode):
            updated_lots.append(node.data)
        if isinstance(node, StockNode):
            updated_stocks.append(node.data)
        if isinstance(node, StockTransformNode):
            updated_stock_transforms.append(node.data)
        if isinstance(node, TicketSourceNode):
            updated_ticket_sources.append(node.data)
        if isinstance(node, TicketNode):
            updated_tickets.append(node.data)

    for lot in updated_lots:
        # save a lot event with the current modification
        update_event = CarbureLotEvent(
            event_type=CarbureLotEvent.UPDATED_BY_ADMIN,
            lot=lot,
            user=request.user,
            metadata=node.diff,
        )

        # add a comment to the lot
        update_comment = CarbureLotComment(
            entity_id=entity_id,
            user=request.user,
            lot=lot,
            comment=comment,
            comment_type=CarbureLotComment.ADMIN,
            is_visible_by_admin=True,
            is_visible_by_auditor=True,
        )

        update_events.append(update_event)
        update_comments.append(update_comment)

    # run sanity checks in memory so we don't modify the current errors
    sanity_check_errors, _ = bulk_sanity_checks(updated_lots, dry_run=True)
    blocking_errors = [error for error in sanity_check_errors if error.is_blocking]

    # # do not modify the database if there are any blocking errors in the modified lots
    if len(blocking_errors) > 0:
        errors_by_lot = group_errors_by_lot(blocking_errors)
        return ErrorResponse(400, UpdateManyError.SANITY_CHECKS_NOT_PASSED, {"errors": errors_by_lot})

    if not dry_run:
        pass
        # @TODO actually apply the changes in the DB for all models
        # save everything in the database in one single transaction
        # with transaction.atomic():
        #     GenericError.objects.filter(lot__in=lots).delete()
        #     GenericError.objects.bulk_create(sanity_check_errors)
        #     CarbureLot.objects.bulk_update(lots, update_fields)
        #     CarbureLotEvent.objects.bulk_create(update_events)
        #     CarbureLotComment.objects.bulk_create(update_comments)

    updates = []
    errors_by_lot = group_errors_by_lot(sanity_check_errors)
    for node in updated_nodes:
        errors = errors_by_lot.get(node.data.id, [])
        updates.append({"node": node.serialize(), "diff": node.diff, "owner": node.owner, "errors": errors})

    return SuccessResponse({"updates": updates})


# grab only the values that are defined on the form data
# and return the list of CarbureLot fields that were changed
def get_update_data(form_data):
    update_data = {}
    quantity_data = {}
    udpate_fields = []

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

        if field == "quantity":
            udpate_fields += ["volume", "weight", "lhv_amount"]
        elif field != "unit":
            udpate_fields += [field]

    return update_data, quantity_data, udpate_fields


def group_errors_by_lot(errors):
    errors_by_lot = {}
    for error in errors:
        if error.lot_id not in errors_by_lot:
            errors_by_lot[error.lot_id] = []
        errors_by_lot[error.lot_id].append(error)
    for lot_id, errors in errors_by_lot.items():
        errors_by_lot[lot_id] = GenericErrorSerializer(errors_by_lot[lot_id], many=True).data
    return errors_by_lot


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
