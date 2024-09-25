from django.db.models.query_utils import Q

from core.models import CarbureLot, CarbureStock
from core.serializers import CarbureLotPublicSerializer, CarbureStockPublicSerializer


def get_lot_parents(lot, entity):
    parents = {"parent_lot": None, "parent_stock": None}
    if lot.parent_lot and (
        lot.parent_lot.added_by == entity
        or lot.parent_lot.carbure_supplier == entity
        or lot.parent_lot.carbure_client == entity
    ):
        parents["parent_lot"] = CarbureLotPublicSerializer(lot.parent_lot).data
    if lot.parent_stock and (lot.parent_stock.carbure_client == entity):
        parents["parent_stock"] = CarbureStockPublicSerializer(lot.parent_stock).data
    return parents


def get_lot_children(lot, entity):
    children = {"children_lot": [], "children_stock": []}

    can_access_lot = Q(added_by=entity) | Q(carbure_supplier=entity) | Q(carbure_client=entity)
    children_lot = (
        CarbureLot.objects.filter(parent_lot=lot)
        .exclude(lot_status=CarbureLot.DELETED)
        .filter(can_access_lot)
        .select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_vendor",
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
        )
    )

    if children_lot.count() > 0:
        children["children_lot"] = CarbureLotPublicSerializer(children_lot, many=True).data

    can_access_stock = Q(carbure_client=entity)
    children_stock = (
        CarbureStock.objects.filter(parent_lot=lot)
        .filter(can_access_stock)
        .select_related(
            "parent_lot",
            "parent_transformation",
            "biofuel",
            "feedstock",
            "country_of_origin",
            "depot",
            "depot__country",
            "carbure_production_site",
            "carbure_production_site__country",
            "production_country",
            "carbure_client",
            "carbure_supplier",
        )
    )

    if children_stock.count() > 0:
        children["children_stock"] = CarbureStockPublicSerializer(children_stock, many=True).data

    return children
