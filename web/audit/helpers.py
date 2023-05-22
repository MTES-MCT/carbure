from django.db.models.query_utils import Q

from core.models import (
    CarbureLot,
    UserRights,
)


def get_auditor_lots(request):
    rights = request.session.get("rights")
    allowed_entities = [
        entity for entity in rights if rights[entity] == UserRights.AUDITOR
    ]

    lots = CarbureLot.objects.select_related(
        "carbure_producer",
        "carbure_supplier",
        "carbure_client",
        "added_by",
        "carbure_production_site",
        "carbure_production_site__producer",
        "carbure_production_site__country",
        "production_country",
        "carbure_dispatch_site",
        "carbure_dispatch_site__country",
        "dispatch_site_country",
        "carbure_delivery_site",
        "carbure_delivery_site__country",
        "delivery_site_country",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "parent_lot",
        "parent_stock",
        "parent_stock__carbure_client",
        "parent_stock__carbure_supplier",
        "parent_stock__feedstock",
        "parent_stock__biofuel",
        "parent_stock__depot",
        "parent_stock__country_of_origin",
        "parent_stock__production_country",
    ).prefetch_related(
        "genericerror_set", "carbure_production_site__productionsitecertificate_set"
    )

    lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    return lots.filter(
        Q(carbure_client__in=allowed_entities)
        | Q(carbure_supplier__in=allowed_entities)
        | Q(added_by__in=allowed_entities)
    )
