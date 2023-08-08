import os
import datetime
import calendar
from multiprocessing.context import Process
from dateutil.relativedelta import relativedelta
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F, OuterRef, Subquery
from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q
from django.http.response import HttpResponse, JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from core.common import try_get_certificate, try_get_double_counting_certificate

from core.ign_distance import get_distance
from core.models import (
    Biocarburant,
    CarbureLot,
    CarbureLotComment,
    CarbureStock,
    CarbureStockEvent,
    CarbureStockTransformation,
    Depot,
    Entity,
    MatierePremiere,
    Pays,
    TransactionDistance,
    UserRights,
)
from core.models import GenericError
from core.serializers import (
    CarbureLotAdminSerializer,
    CarbureLotCommentSerializer,
    CarbureLotEventSerializer,
    CarbureLotPublicSerializer,
    CarbureStockEventSerializer,
    CarbureStockPublicSerializer,
    GenericErrorAdminSerializer,
    GenericErrorSerializer,
)
from core.xlsx_v3 import export_carbure_lots, export_carbure_stock


sort_key_to_django_field = {
    "period": "delivery_date",
    "feedstock": "feedstock__name",
    "ghg_reduction": "ghg_reduction",
    "volume": "volume",
    "country_of_origin": "country_of_origin__name",
    "added_by": "added_by__name",
}

stock_sort_key_to_django_field = {
    "feedstock": "feedstock__name",
    "ghg_reduction": "ghg_reduction",
    "volume": "remaining_volume",
    "country_of_origin": "country_of_origin__name",
}


def get_entity_stock(entity_id):
    return CarbureStock.objects.filter(carbure_client_id=entity_id).select_related(
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


# admin only
def get_all_stock():
    return CarbureStock.objects.all().select_related(
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


def get_auditor_stock(auditor):
    rights = UserRights.objects.filter(user=auditor, role=UserRights.AUDITOR)
    entities = [r.entity_id for r in rights]
    return CarbureStock.objects.filter(carbure_client__in=entities).select_related(
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


def get_entity_lots_by_status(entity, status=None, export=False):
    lots = CarbureLot.objects.select_related(
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
    if not export:
        lots = lots.prefetch_related("genericerror_set", "carbure_production_site__productionsitecertificate_set")
    if status == "DRAFTS":
        lots = lots.filter(added_by=entity, lot_status=CarbureLot.DRAFT)
    elif status == "IN":
        lots = lots.filter(carbure_client=entity).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    elif status == "OUT":
        lots = lots.filter(carbure_supplier=entity).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    elif status == "DECLARATION":
        lots = lots.filter(Q(carbure_supplier=entity) | Q(carbure_client=entity)).exclude(
            lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED]
        )
    else:
        lots = lots.filter(Q(added_by=entity) | Q(carbure_supplier=entity) | Q(carbure_client=entity))
    return lots


def get_lots_with_metadata(lots, entity, query):
    export = query.get("export", False)
    limit = query.get("limit", None)
    from_idx = query.get("from_idx", "0")

    # filtering
    lots = filter_lots(lots, query, entity)
    # sorting
    lots = sort_lots(lots, query)

    if export:
        file_location = export_carbure_lots(entity, lots)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (file_location)
        return response

    # pagination
    from_idx = int(from_idx)
    returned = lots[from_idx:]
    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    total_errors, total_deadline = count_lots_of_interest(lots, entity)

    # enrich dataset with additional metadata
    if entity.entity_type in (Entity.ADMIN, Entity.AUDITOR):
        serializer = CarbureLotAdminSerializer(returned, many=True)
    else:
        serializer = CarbureLotPublicSerializer(returned, many=True)

    data = {}
    data["lots"] = serializer.data
    data["from"] = from_idx
    data["returned"] = returned.count()
    data["total"] = lots.count()
    data["total_errors"] = total_errors
    data["total_deadline"] = total_deadline
    data["errors"] = get_lots_errors(returned, entity)
    data["ids"] = list(lots.values_list("id", flat=True))
    return JsonResponse({"status": "success", "data": data})


def get_current_deadline():
    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)
    return deadline_date


def get_stock_with_errors(stock, entity_id=None):
    if entity_id is None:
        filter = Q(lot=OuterRef("pk"))
    else:
        filter = Q(lot=OuterRef("pk")) & (
            Q(parent_lot__added_by_id=entity_id, display_to_creator=True)
            | Q(parent_lot__carbure_client_id=entity_id, display_to_recipient=True)
        )
    tx_errors = GenericError.objects.filter(filter).values("lot").annotate(errors=Count("id")).values("errors")
    return stock.annotate(errors=Subquery(tx_errors)).filter(errors__gt=0)


def get_lots_with_errors(lots, entity, will_aggregate=False):
    if will_aggregate:
        # use a subquery so we can later do aggregations on this queryset without wrecking the results
        tx_errors = GenericError.objects.filter(lot=OuterRef("pk"))
        if entity.entity_type == Entity.ADMIN:
            filter = Q(display_to_admin=True, acked_by_admin=False)
        elif entity.entity_type == Entity.AUDITOR:
            filter = Q(display_to_auditor=True, acked_by_auditor=False)
        else:
            filter = Q(lot__added_by=entity, display_to_creator=True, acked_by_creator=False) | Q(
                lot__carbure_client=entity,
                display_to_recipient=True,
                acked_by_recipient=False,
            )
        tx_errors = tx_errors.filter(filter)
        tx_errors = tx_errors.values("lot").annotate(errors=Count("id")).values("errors")
        return lots.annotate(errors=Subquery(tx_errors)).filter(errors__gt=0)
    else:
        if entity.entity_type == Entity.ADMIN:
            filter = Q(genericerror__display_to_admin=True, genericerror__acked_by_admin=False)
            counter = Count("genericerror", filter=filter)
        elif entity.entity_type == Entity.AUDITOR:
            filter = Q(
                genericerror__display_to_auditor=True,
                genericerror__acked_by_auditor=False,
            )
            counter = Count("genericerror", filter=filter)
        else:
            filter = Q(
                added_by=entity,
                genericerror__display_to_creator=True,
                genericerror__acked_by_creator=False,
            ) | Q(
                carbure_client=entity,
                genericerror__display_to_recipient=True,
                genericerror__acked_by_recipient=False,
            )
            counter = Count("genericerror", filter=filter)
        return lots.annotate(errors=counter).filter(errors__gt=0)


def get_lots_with_deadline(lots, deadline=get_current_deadline()):
    affected_date = deadline - relativedelta(months=1)
    period = affected_date.year * 100 + affected_date.month
    return lots.filter(
        period=period,
        lot_status__in=[CarbureLot.DRAFT, CarbureLot.REJECTED, CarbureLot.PENDING],
    )


def filter_lots(lots, query, entity=None, will_aggregate=False, blacklist=[]):
    year = query.get("year", False)
    periods = query.getlist("periods", [])
    production_sites = query.getlist("production_sites", [])
    delivery_sites = query.getlist("delivery_sites", [])
    feedstocks = query.getlist("feedstocks", [])
    countries_of_origin = query.getlist("countries_of_origin", [])
    biofuels = query.getlist("biofuels", [])
    clients = query.getlist("clients", [])
    suppliers = query.getlist("suppliers", [])
    correction_status = query.getlist("correction_status", [])
    delivery_types = query.getlist("delivery_types", [])
    errors = query.getlist("errors", [])
    search = query.get("query", False)
    selection = query.getlist("selection", [])
    history = query.get("history", False)
    correction = query.get("correction", False)
    client_types = query.getlist("client_types", [])
    lot_status = query.getlist("lot_status", False)
    category = query.get("category", False)
    scores = query.getlist("scores", [])
    added_by = query.getlist("added_by", [])
    conformity = query.getlist("conformity", [])
    ml = query.getlist("ml_scoring", False)

    # selection overrides all other filters
    if len(selection) > 0:
        return lots.filter(pk__in=selection)

    if correction == "true":
        lots = lots.filter(
            Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]) | Q(lot_status=CarbureLot.REJECTED)
        )
    elif history != "true" and entity.entity_type not in (Entity.ADMIN, Entity.AUDITOR):
        lots = lots.exclude(lot_status__in=[CarbureLot.FROZEN, CarbureLot.ACCEPTED])

    if lot_status and "lot_status" not in blacklist:
        lots = lots.filter(lot_status__in=lot_status)

    if year and "year" not in blacklist:
        lots = lots.filter(year=year)
    if len(delivery_types) > 0 and "delivery_types" not in blacklist:
        lots = lots.filter(delivery_type__in=delivery_types)
    if len(correction_status) > 0 and "correction_status" not in blacklist:
        lots = lots.filter(correction_status__in=correction_status)
    if len(periods) > 0 and "periods" not in blacklist:
        lots = lots.filter(period__in=periods)
    if len(feedstocks) > 0 and "feedstocks" not in blacklist:
        lots = lots.filter(feedstock__code__in=feedstocks)
    if len(biofuels) > 0 and "biofuels" not in blacklist:
        lots = lots.filter(biofuel__code__in=biofuels)
    if len(countries_of_origin) > 0 and "countries_of_origin" not in blacklist:
        lots = lots.filter(country_of_origin__code_pays__in=countries_of_origin)
    if len(scores):
        lots = lots.filter(data_reliability_score__in=scores)
    if category == "stocks":
        lots = lots.filter(parent_stock__isnull=False)
    elif category == "imported":
        lots = lots.filter(parent_stock__isnull=True)
    else:
        pass

    if len(production_sites) > 0 and "production_sites" not in blacklist:
        production_site_filter = Q(carbure_production_site__name__in=production_sites) | Q(
            unknown_production_site__in=production_sites
        )
        if "UNKNOWN" in production_sites:
            production_site_filter = production_site_filter | (
                Q(carbure_production_site__isnull=True) & (Q(unknown_production_site=None) | Q(unknown_production_site=""))
            )
        lots = lots.filter(production_site_filter)

    if len(delivery_sites) > 0 and "delivery_sites" not in blacklist:
        delivery_site_filter = Q(carbure_delivery_site__name__in=delivery_sites) | Q(
            unknown_delivery_site__in=delivery_sites
        )
        if "UNKNOWN" in delivery_sites:
            delivery_site_filter = delivery_site_filter | (
                Q(carbure_delivery_site__isnull=True) & (Q(unknown_delivery_site=None) | Q(unknown_delivery_site=""))
            )
        lots = lots.filter(delivery_site_filter)

    if len(clients) > 0 and "clients" not in blacklist:
        client_filter = Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients)
        if "UNKNOWN" in clients:
            client_filter = client_filter | (
                Q(carbure_client__isnull=True) & (Q(unknown_client=None) | Q(unknown_client=""))
            )
        lots = lots.filter(client_filter)

    if len(suppliers) > 0 and "suppliers" not in blacklist:
        supplier_filter = Q(carbure_supplier__name__in=suppliers) | Q(unknown_supplier__in=suppliers)
        if "UNKNOWN" in suppliers:
            supplier_filter = supplier_filter | (
                Q(carbure_supplier__isnull=True) & (Q(unknown_supplier=None) | Q(unknown_supplier=""))
            )
        lots = lots.filter(supplier_filter)

    if len(client_types) > 0 and "client_types" not in blacklist:
        client_type_filter = Q(carbure_client__entity_type__in=client_types)
        if Entity.UNKNOWN in client_types:
            client_type_filter = client_type_filter | Q(carbure_client__isnull=True)
        lots = lots.filter(client_type_filter)

    if len(errors) > 0 and "errors" not in blacklist:
        lots = lots.filter(genericerror__error__in=errors)

    if len(added_by) > 0 and "added_by" not in blacklist:
        lots = lots.filter(added_by__name__in=added_by)

    if len(conformity) > 0 and "conformity" not in blacklist:
        lots = lots.filter(audit_status__in=conformity)

    if ml and "ml_scoring" not in blacklist:
        if ml == "KO":
            lots = lots.filter(ml_scoring_requested=True)
        else:
            lots = lots.filter(ml_scoring_requested=False)

    if search and "query" not in blacklist:
        lots = lots.filter(
            Q(feedstock__name__icontains=search)
            | Q(biofuel__name__icontains=search)
            | Q(carbure_producer__name__icontains=search)
            | Q(unknown_producer__icontains=search)
            | Q(carbure_id__icontains=search)
            | Q(country_of_origin__name__icontains=search)
            | Q(carbure_client__name__icontains=search)
            | Q(unknown_client__icontains=search)
            | Q(carbure_delivery_site__name__icontains=search)
            | Q(unknown_delivery_site__icontains=search)
            | Q(free_field__icontains=search)
            | Q(transport_document_reference__icontains=search)
            | Q(production_site_double_counting_certificate__icontains=search)
        )

    invalid = query.get("invalid", False)
    deadline = query.get("deadline", False)

    if invalid == "true":
        lots = get_lots_with_errors(lots, entity, will_aggregate)
    if deadline == "true":
        lots = get_lots_with_deadline(lots)
    return lots


def count_lots_of_interest(lots, entity):
    error_lots = get_lots_with_errors(lots, entity)
    deadline_lots = get_lots_with_deadline(lots)
    return error_lots.count(), deadline_lots.count()


def sort_lots(lots, query):
    sort_by = query.get("sort_by", False)
    order = query.get("order", False)

    if not sort_by:
        lots = lots.order_by("-id")
    elif sort_by in sort_key_to_django_field:
        key = sort_key_to_django_field[sort_by]
        if order == "desc":
            lots = lots.order_by("-%s" % key)
        else:
            lots = lots.order_by(key)
    elif sort_by == "biofuel":
        if order == "desc":
            lots = lots.order_by("-biofuel__name", "-volume")
        else:
            lots = lots.order_by("biofuel__name", "volume")
    elif sort_by == "client":
        lots = lots.annotate(client=Coalesce("carbure_client__name", "unknown_client"))
        if order == "desc":
            lots = lots.order_by("-client")
        else:
            lots = lots.order_by("client")
    elif sort_by == "supplier":
        lots = lots.annotate(vendor=Coalesce("carbure_supplier__name", "unknown_supplier"))
        if order == "desc":
            lots = lots.order_by("-supplier")
        else:
            lots = lots.order_by("supplier")
    return lots


def prepare_filters(filter_list):
    return sorted(list(set([i for i in filter_list if i is not None])))


UNKNOWN_VALUE = "UNKNOWN"


def get_lots_filters_data(lots, query, entity, field):
    lots = filter_lots(lots, query, entity, blacklist=[field])

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


def get_stock_filters_data(stock, query, field):
    stock = filter_stock(stock, query, blacklist=[field])

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


def get_stock_with_metadata(stock, query):
    export = query.get("export", False)
    limit = query.get("limit", None)
    from_idx = query.get("from_idx", "0")

    # filtering
    stock = filter_stock(stock, query)
    # sorting
    stock = sort_stock(stock, query)

    # pagination
    from_idx = int(from_idx)
    returned = stock[from_idx:]
    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    # enrich dataset with additional metadata
    serializer = CarbureStockPublicSerializer(returned, many=True)
    data = {}
    data["stocks"] = serializer.data
    data["total"] = stock.count()
    data["returned"] = returned.count()
    data["from"] = from_idx
    data["ids"] = list(stock.values_list("id", flat=True))

    if not export:
        return JsonResponse({"status": "success", "data": data})
    else:
        file_location = export_carbure_stock(returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (file_location)
        return response


def filter_stock(stock, query, blacklist=[]):
    periods = query.getlist("periods", [])
    depots = query.getlist("depots", [])
    feedstocks = query.getlist("feedstocks", [])
    countries_of_origin = query.getlist("countries_of_origin", [])
    biofuels = query.getlist("biofuels", [])
    suppliers = query.getlist("suppliers", [])
    production_sites = query.getlist("production_sites", [])
    search = query.get("query", False)
    selection = query.getlist("selection", [])
    history = query.get("history", False)
    clients = query.getlist("clients", [])

    if history != "true":
        stock = stock.filter(remaining_volume__gt=0)
    if len(selection) > 0:
        stock = stock.filter(pk__in=selection)
    if len(periods) > 0 and "periods" not in blacklist:
        stock = stock.filter(
            Q(parent_lot__period__in=periods) | Q(parent_transformation__source_stock__parent_lot__period__in=periods)
        )
    if len(feedstocks) > 0 and "feedstocks" not in blacklist:
        stock = stock.filter(feedstock__code__in=feedstocks)
    if len(biofuels) > 0 and "biofuels" not in blacklist:
        stock = stock.filter(biofuel__code__in=biofuels)
    if len(countries_of_origin) > 0 and "countries_of_origin" not in blacklist:
        stock = stock.filter(country_of_origin__code_pays__in=countries_of_origin)
    if len(depots) > 0 and "depots" not in blacklist:
        stock = stock.filter(depot__name__in=depots)
    if len(suppliers) > 0 and "suppliers" not in blacklist:
        stock = stock.filter(Q(carbure_supplier__name__in=suppliers) | Q(unknown_supplier__in=suppliers))
    if len(production_sites) > 0 and "production_sites" not in blacklist:
        stock = stock.filter(
            Q(carbure_production_site__name__in=production_sites) | Q(unknown_production_site__in=production_sites)
        )
    if len(clients):
        stock = stock.filter(carbure_client__name__in=clients)
    if search and "query" not in blacklist:
        stock = stock.filter(
            Q(feedstock__name__icontains=search)
            | Q(biofuel__name__icontains=search)
            | Q(carbure_id__icontains=search)
            | Q(country_of_origin__name__icontains=search)
            | Q(depot__name__icontains=search)
            | Q(parent_lot__free_field__icontains=search)
            | Q(parent_lot__transport_document_reference__icontains=search)
        )
    return stock


def sort_stock(stock, query):
    sort_by = query.get("sort_by", False)
    order = query.get("order", False)

    if not sort_by:
        stock = stock.order_by("-id")
    elif sort_by in stock_sort_key_to_django_field:
        key = stock_sort_key_to_django_field[sort_by]
        if order == "desc":
            stock = stock.order_by("-%s" % key)
        else:
            stock = stock.order_by(key)
    elif sort_by == "biofuel":
        if order == "desc":
            stock = stock.order_by("-biofuel__name", "-remaining_volume")
        else:
            stock = stock.order_by("biofuel__name", "remaining_volume")
    elif sort_by == "vendor":
        stock = stock.annotate(vendor=Coalesce("carbure_supplier__name", "unknown_supplier"))
        if order == "desc":
            stock = stock.order_by("-vendor")
        else:
            stock = stock.order_by("vendor")
    return stock


def get_lot_errors(lot, entity=None):
    errors = []
    if entity.entity_type == Entity.ADMIN:
        errors = lot.genericerror_set.filter(display_to_admin=True)
        return GenericErrorAdminSerializer(errors, many=True, read_only=True).data
    elif entity.entity_type == Entity.AUDITOR:
        errors = lot.genericerror_set.filter(display_to_auditor=True)
        return GenericErrorAdminSerializer(errors, many=True, read_only=True).data
    else:
        errors = GenericError.objects.filter(lot_id=lot.id)
        errors = errors.filter(
            Q(lot__added_by=entity, display_to_creator=True) | Q(lot__carbure_client=entity, display_to_recipient=True)
        )
        return GenericErrorSerializer(errors, many=True, read_only=True).data


def get_lots_errors(lots, entity):
    lot_ids = list(lots.values_list("id", flat=True))
    errors = GenericError.objects.filter(lot_id__in=lot_ids)
    if entity.entity_type == Entity.ADMIN:
        errors = errors.filter(display_to_admin=True, acked_by_admin=False)
    elif entity.entity_type == Entity.AUDITOR:
        errors = errors.filter(display_to_auditor=True, acked_by_auditor=False)
    else:
        errors = errors.filter(
            Q(lot__added_by=entity, display_to_creator=True, acked_by_creator=False)
            | Q(
                lot__carbure_client=entity,
                display_to_recipient=True,
                acked_by_recipient=False,
            )
        )
    data = {}
    for error in errors.values("lot_id", "error", "is_blocking", "field", "value", "extra", "fields").iterator():
        if error["lot_id"] not in data:
            data[error["lot_id"]] = []
        data[error["lot_id"]].append(GenericErrorSerializer(error).data)
    return data


def get_lot_updates(lot, entity=None):
    if lot is None:
        return []

    context = {"visible_users": None}

    # list the only users email addresses that should be sent to the frontend
    if entity is not None:
        context["visible_users"] = (
            UserRights.objects.filter(entity__in=(lot.added_by, lot.carbure_supplier, lot.carbure_client))
            .values_list("user__email", flat=True)
            .distinct()
        )

    return CarbureLotEventSerializer(lot.carburelotevent_set.all(), many=True, context=context).data


def get_stock_events(lot, entity=None):
    if lot is None:
        return []
    return CarbureStockEventSerializer(lot.carburelotevent_set.all(), many=True).data


def get_lot_comments(lot, entity=None):
    if lot is None:
        return []
    comments = lot.carburelotcomment_set.filter(comment_type=CarbureLotComment.REGULAR)
    return CarbureLotCommentSerializer(comments, many=True).data


def get_transaction_distance(lot):
    url_link = "https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=driving"
    res = {"distance": -1, "link": "", "error": None, "source": None}

    if not lot.carbure_production_site:
        res["error"] = "PRODUCTION_SITE_NOT_IN_CARBURE"
        return res
    if not lot.carbure_delivery_site:
        res["error"] = "DELIVERY_SITE_NOT_IN_CARBURE"
        return res
    starting_point = lot.carbure_production_site.gps_coordinates
    delivery_point = lot.carbure_delivery_site.gps_coordinates
    if not starting_point:
        res["error"] = "PRODUCTION_SITE_COORDINATES_NOT_IN_CARBURE"
        return res
    if not delivery_point:
        res["error"] = "DELIVERY_SITE_COORDINATES_NOT_IN_CARBURE"
        return res
    try:
        td = TransactionDistance.objects.get(starting_point=starting_point, delivery_point=delivery_point)
        res["link"] = url_link % (starting_point, delivery_point)
        res["distance"] = td.distance
        res["source"] = "DB"
        return res
    except:
        # not found, launch in background for next time
        p = Process(target=get_distance, args=(starting_point, delivery_point))
        p.start()
        res["error"] = "DISTANCE_NOT_IN_CACHE"
        return res


def send_email_declaration_validated(declaration):
    email_subject = "Carbure - Votre Déclaration de Durabilité a été validée"
    text_message = """
    Bonjour,

    Votre Déclaration de Durabilité pour la période %s a bien été prise en compte.

    Merci,
    L'équipe CarbuRe
    """
    env = os.getenv("IMAGE_TAG", False)
    if env != "prod":
        # send only to staff / superuser
        recipients = [r.user.email for r in UserRights.objects.filter(entity=declaration.entity, user__is_staff=True)]
    else:
        # PROD
        recipients = [
            r.user.email
            for r in UserRights.objects.filter(
                entity=declaration.entity,
                user__is_staff=False,
                user__is_superuser=False,
            ).exclude(role__in=[UserRights.AUDITOR, UserRights.RO])
        ]

    period = declaration.period.strftime("%Y-%m")
    msg = EmailMultiAlternatives(
        subject=email_subject,
        body=text_message % (period),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    msg.send()


def send_email_declaration_invalidated(declaration):
    email_subject = "Carbure - Votre Déclaration de Durabilité a été annulée"
    text_message = """
    Bonjour,

    Votre Déclaration de Durabilité pour la période %s a bien été annulée.
    Vous pouvez désormais éditer ou demander des corrections sur les lots concernés avant de la soumettre une nouvelle fois.

    Merci,
    L'équipe CarbuRe
    """
    env = os.getenv("IMAGE_TAG", False)
    if env != "prod":
        # send only to staff / superuser
        recipients = [r.user.email for r in UserRights.objects.filter(entity=declaration.entity, user__is_staff=True)]
    else:
        # PROD
        recipients = [
            r.user.email
            for r in UserRights.objects.filter(
                entity=declaration.entity,
                user__is_staff=False,
                user__is_superuser=False,
            ).exclude(role__in=[UserRights.AUDITOR, UserRights.RO])
        ]

    period = declaration.period.strftime("%Y-%m")
    msg = EmailMultiAlternatives(
        subject=email_subject,
        body=text_message % (period),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    msg.send()


def get_lots_summary_data(lots, entity, short=False):
    data = {
        "count": lots.count(),
        "total_volume": lots.aggregate(Sum("volume"))["volume__sum"] or 0,
        "total_weight": lots.aggregate(Sum("weight"))["weight__sum"] or 0,
        "total_lhv_amount": lots.aggregate(Sum("lhv_amount"))["lhv_amount__sum"] or 0,
    }

    if short:
        return data

    pending_filter = Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED]) | Q(
        correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]
    )

    lots_in = (
        lots.filter(carbure_client=entity)
        .annotate(
            supplier=Coalesce("carbure_supplier__name", "unknown_supplier"),
            biofuel_code=F("biofuel__code"),
        )
        .values("supplier", "biofuel_code", "delivery_type")
        .annotate(
            volume_sum=Sum("volume"),
            weight_sum=Sum("weight"),
            lhv_amount_sum=Sum("lhv_amount"),
            avg_ghg_reduction=Sum(F("volume") * F("ghg_reduction_red_ii")) / Sum("volume"),
            total=Count("id"),
            pending=Count("id", filter=pending_filter),
        )
        .order_by()
    )

    lots_out = (
        lots.filter(Q(carbure_supplier=entity) | Q(carbure_vendor=entity))
        .exclude(carbure_client=entity)
        .annotate(
            client=Coalesce("carbure_client__name", "unknown_client"),
            biofuel_code=F("biofuel__code"),
        )
        .values("client", "biofuel_code")
        .annotate(
            volume_sum=Sum("volume"),
            weight_sum=Sum("weight"),
            lhv_amount_sum=Sum("lhv_amount"),
            avg_ghg_reduction=Sum(F("volume") * F("ghg_reduction_red_ii")) / Sum("volume"),
            total=Count("id"),
            pending=Count("id", filter=pending_filter),
        )
        .order_by()
    )

    data["in"] = list(lots_in)
    data["out"] = list(lots_out)
    return data


def get_stocks_summary_data(stocks, entity_id=None, short=False):
    data = {
        "count": stocks.count(),
        "total_remaining_volume": stocks.aggregate(Sum("remaining_volume"))["remaining_volume__sum"] or 0,
        "total_remaining_weight": stocks.aggregate(Sum("remaining_weight"))["remaining_weight__sum"] or 0,
        "total_remaining_lhv_amount": stocks.aggregate(Sum("remaining_lhv_amount"))["remaining_lhv_amount__sum"] or 0,
    }

    if short:
        return data
    if entity_id is not None:
        stocks = stocks.filter(carbure_client_id=entity_id)
    stock_summary = (
        stocks.annotate(
            supplier=Coalesce("carbure_supplier__name", "unknown_supplier"),
            biofuel_code=F("biofuel__code"),
        )
        .values("supplier", "biofuel_code")
        .annotate(
            remaining_volume_sum=Sum("remaining_volume"),
            remaining_weight_sum=Sum("remaining_weight"),
            remaining_lhv_amount_sum=Sum("remaining_lhv_amount"),
            avg_ghg_reduction=Sum(F("remaining_volume") * F("ghg_reduction_red_ii")) / Sum("remaining_volume"),
            total=Count("id"),
        )
        .order_by()
    )
    data["stock"] = list(stock_summary)
    return data


def handle_eth_to_etbe_transformation(user, stock, transformation):
    required_fields = [
        "volume_ethanol",
        "volume_etbe",
        "volume_denaturant",
        "volume_etbe_eligible",
    ]
    for f in required_fields:
        if f not in transformation:
            return JsonResponse(
                {"status": "error", "message": "Could not find field %s" % (f)},
                status=400,
            )

    volume_ethanol = transformation["volume_ethanol"]
    volume_etbe = transformation["volume_etbe"]
    volume_denaturant = transformation["volume_denaturant"]
    volume_etbe_eligible = transformation["volume_etbe_eligible"]
    etbe = Biocarburant.objects.get(code="ETBE")

    # check if source stock is Ethanol
    if stock.biofuel.code != "ETH":
        return JsonResponse({"status": "error", "message": "Source stock is not Ethanol"}, status=400)

    volume_ethanol = round(float(volume_ethanol), 2)
    volume_etbe = round(float(volume_etbe), 2)
    volume_etbe_eligible = round(float(volume_etbe_eligible), 2)
    volume_denaturant = round(float(volume_denaturant), 2)

    # check available volume
    if stock.remaining_volume < volume_ethanol:
        return JsonResponse(
            {
                "status": "error",
                "message": "Volume Ethanol is higher than available volume",
            },
            status=400,
        )

    stock.remaining_volume = round(stock.remaining_volume - volume_ethanol)
    stock.remaining_weight = stock.get_weight()
    stock.remaining_lhv_amount = stock.get_lhv_amount()
    stock.save()

    old_stock_id = stock.id
    new_stock = stock
    new_stock.pk = None
    new_stock.biofuel = etbe
    new_stock.remaining_volume = volume_etbe
    new_stock.remaining_weight = new_stock.get_weight()
    new_stock.remaining_lhv_amount = new_stock.get_lhv_amount()
    new_stock.parent_lot = None
    new_stock.save()

    cst = CarbureStockTransformation()
    cst.transformation_type = CarbureStockTransformation.ETH_ETBE
    cst.source_stock_id = old_stock_id
    cst.dest_stock = new_stock
    cst.volume_deducted_from_source = volume_ethanol
    cst.volume_destination = volume_etbe
    cst.transformed_by = user
    cst.entity = stock.carbure_client
    cst.metadata = {
        "volume_denaturant": volume_denaturant,
        "volume_etbe_eligible": volume_etbe_eligible,
    }
    cst.save()

    new_stock.parent_transformation = cst
    new_stock.carbure_id = "%sT%d" % (stock.carbure_id, new_stock.id)
    new_stock.save()

    # create events
    e = CarbureStockEvent()
    e.event_type = CarbureStockEvent.TRANSFORMED
    e.stock = stock
    e.user = user
    e.save()


def get_known_certificates(lot):
    d = {
        "production_site_certificate": None,
        "supplier_certificate": None,
        "vendor_certificate": None,
        "production_site_double_counting_certificate": None,
    }
    # production site certificate
    if lot.production_site_certificate:
        d["production_site_certificate"] = try_get_certificate(lot.production_site_certificate)
    if lot.supplier_certificate:
        d["supplier_certificate"] = try_get_certificate(lot.supplier_certificate)
    if lot.vendor_certificate:
        d["vendor_certificate"] = try_get_certificate(lot.vendor_certificate)
    if lot.production_site_double_counting_certificate:
        d["production_site_double_counting_certificate"] = try_get_double_counting_certificate(
            lot.production_site_double_counting_certificate, lot.carbure_production_site
        )
    return d
