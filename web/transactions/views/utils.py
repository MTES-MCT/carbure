from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q

from core.models import (
    Biocarburant,
    CarbureLot,
    CarbureStock,
    Depot,
    Entity,
    MatierePremiere,
    Pays,
    UserRights,
)
from core.serializers import CarbureLotPublicSerializer, CarbureStockPublicSerializer

UNKNOWN_VALUE = "UNKNOWN"


def prepare_filters(filter_list):
    return sorted({i for i in filter_list if i is not None})


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


def get_lots_filters_data(lots, field):
    if field == "feedstocks":
        lot_feedstocks = lots.values("feedstock__id").distinct()
        feedstocks = MatierePremiere.objects.filter(id__in=lot_feedstocks)
        return prepare_filters(feedstocks.values_list("code", flat=True))

    if field == "biofuels":
        lot_biofuels = lots.values("biofuel__id").distinct()
        biofuels = Biocarburant.objects.filter(id__in=lot_biofuels).values_list("code", flat=True)
        return prepare_filters(biofuels)

    if field == "countries_of_origin":
        lot_countries = lots.values("country_of_origin").distinct()
        countries = Pays.objects.filter(id__in=lot_countries).values_list("code_pays", flat=True)
        return prepare_filters(countries)

    if field == "periods":
        periods = lots.values_list("period", flat=True).distinct()
        return prepare_filters(periods)

    if field == "errors":
        generic_errors = lots.values_list("genericerror__error", flat=True).exclude(genericerror__error=None).distinct()
        return prepare_filters(generic_errors)

    if field == "added_by":
        added_by = lots.values_list("added_by__name", flat=True).distinct()
        return prepare_filters(added_by)

    if field == "delivery_types":
        delivery_types = lots.values_list("delivery_type", flat=True).distinct()
        return prepare_filters(delivery_types)

    if field == "lot_status":
        lot_status = lots.values_list("lot_status", flat=True).distinct()
        return prepare_filters(lot_status)

    if field == "production_sites":
        production_sites = []
        for item in (
            lots.annotate(production_site=Coalesce("carbure_production_site__name", "unknown_production_site"))
            .values("production_site")
            .distinct()
        ):
            production_sites.append(item["production_site"] or UNKNOWN_VALUE)
        return prepare_filters(production_sites)

    if field == "delivery_sites":
        delivery_sites = []
        for item in (
            lots.annotate(delivery_site=Coalesce("carbure_delivery_site__name", "unknown_delivery_site"))
            .values("delivery_site")
            .distinct()
        ):
            delivery_sites.append(item["delivery_site"] or UNKNOWN_VALUE)
        return prepare_filters(delivery_sites)

    if field == "suppliers":
        suppliers = []
        for item in (
            lots.annotate(supplier=Coalesce("carbure_supplier__name", "unknown_supplier")).values("supplier").distinct()
        ):
            suppliers.append(item["supplier"] or UNKNOWN_VALUE)
        return prepare_filters(suppliers)

    if field == "clients":
        clients = []
        for item in lots.annotate(client=Coalesce("carbure_client__name", "unknown_client")).values("client").distinct():
            clients.append(item["client"] or UNKNOWN_VALUE)
        return prepare_filters(clients)

    if field == "client_types":
        client_types = []
        for item in lots.values("carbure_client__entity_type").distinct():
            client_types.append(item["carbure_client__entity_type"] or Entity.UNKNOWN)
        return prepare_filters(client_types)

    if field == "scores":
        scores = lots.values_list("data_reliability_score", flat=True).distinct()
        return prepare_filters(scores)

    if field == "correction_status":
        corrections = lots.values_list("correction_status", flat=True).distinct()
        return prepare_filters(corrections)

    if field == "conformity":
        conformities = lots.values_list("audit_status", flat=True).distinct()
        return prepare_filters(conformities)

    if field == "ml_scoring":
        return prepare_filters(["KO", "OK"])


def get_stock_filters_data(stock, field):
    # stock = filter_stock(stock, query, blacklist=[field])

    if field == "feedstocks":
        stock_feedstocks = stock.values("feedstock__id").distinct()
        feedstocks = MatierePremiere.objects.filter(id__in=stock_feedstocks).values_list("code", flat=True)
        return prepare_filters(feedstocks)

    if field == "biofuels":
        stock_biofuels = stock.values("biofuel__id").distinct()
        biofuels = Biocarburant.objects.filter(id__in=stock_biofuels).values_list("code")
        return prepare_filters(biofuels)

    if field == "countries_of_origin":
        stock_countries = stock.values("country_of_origin").distinct()
        countries = Pays.objects.filter(id__in=stock_countries).values_list("code_pays", flat=True)
        return prepare_filters(countries)

    if field == "periods":
        set1 = stock.filter(parent_lot__isnull=False).values("parent_lot__period").distinct()
        set2 = (
            stock.filter(parent_transformation__isnull=False)
            .values("parent_transformation__source_stock__parent_lot__period")
            .distinct()
        )
        periods = [s["parent_lot__period"] for s in set1] + [
            s["parent_transformation__source_stock__parent_lot__period"] for s in set2
        ]
        return prepare_filters(periods)

    if field == "depots":
        stock_depots = stock.values("depot__id").distinct()
        depots = Depot.objects.filter(id__in=stock_depots).values_list("name", flat=True)
        return prepare_filters(depots)

    if field == "clients":
        clients = stock.filter(carbure_client__isnull=False).values_list("carbure_client__name", flat=True).distinct()
        return prepare_filters(clients)

    if field == "suppliers":
        suppliers = []
        for item in stock.values("carbure_supplier__name", "unknown_supplier").distinct():
            if item["carbure_supplier__name"] not in ("", None):
                suppliers.append(item["carbure_supplier__name"])
            elif item["unknown_supplier"] not in ("", None):
                suppliers.append(item["unknown_supplier"])
        return prepare_filters(suppliers)

    if field == "production_sites":
        production_sites = []
        for item in stock.values("carbure_production_site__name", "unknown_production_site").distinct():
            if item["carbure_production_site__name"] not in ("", None):
                production_sites.append(item["carbure_production_site__name"])
            elif item["unknown_production_site"] not in ("", None):
                production_sites.append(item["unknown_production_site"])
        return prepare_filters(production_sites)


def get_auditor_lots(request):
    rights = request.session.get("rights")
    allowed_entities = [entity for entity in rights if rights[entity] == UserRights.AUDITOR]

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
    ).prefetch_related("genericerror_set", "carbure_production_site__productionsitecertificate_set")

    lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    return lots.filter(
        Q(carbure_client__in=allowed_entities) | Q(carbure_supplier__in=allowed_entities) | Q(added_by__in=allowed_entities)
    )
