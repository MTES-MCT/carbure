from core.decorators import check_user_rights
from django.http.response import JsonResponse
from core.helpers import get_prefetched_data
from transactions.helpers import try_get_date
from carbure.tasks import background_bulk_scoring, background_bulk_sanity_checks
from core.models import (
    CarbureLot,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockEvent,
    Depot,
    Entity,
    Pays,
    UserRights,
)
import json


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_split(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    payload = request.POST.get("payload", False)
    if not payload:
        return JsonResponse(
            {"status": "error", "message": "Missing payload"}, status=400
        )
    entity = Entity.objects.get(id=entity_id)
    prefetched_data = get_prefetched_data(entity)

    try:
        unserialized = json.loads(payload)
        # expected format: [{stock_id: "L20140-4243-XXX", volume: 3244.33, transport_document_type: 'DAE', transport_document_reference: 'FR221244342WW'
        # dispatch_date: '2021-05-11', carbure_delivery_site_id: None, unknown_delivery_site: "SomeUnknownDepot", delivery_site_country_id: 120,
        # delivery_type: 'EXPORT', carbure_client_id: 12, unknown_client: None, supplier_certificate: "MON_CERTIFICAT"}]
    except:
        return JsonResponse(
            {"status": "error", "message": "Cannot parse payload into JSON"}, status=400
        )

    if not isinstance(unserialized, list):
        return JsonResponse(
            {"status": "error", "message": "Parsed JSON is not a list"}, status=400
        )

    new_lots = []
    for entry in unserialized:
        # check minimum fields
        required_fields = ["stock_id", "volume", "delivery_date"]
        for field in required_fields:
            if field not in entry:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Missing field %s in json object" % (field),
                    },
                    status=400,
                )

        try:
            stock = CarbureStock.objects.get(carbure_id=entry["stock_id"])
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Could not find stock"}, status=400
            )

        if stock.carbure_client_id != int(entity_id):
            return JsonResponse(
                {"status": "forbidden", "message": "Stock does not belong to you"},
                status=403,
            )

        try:
            volume = float(entry["volume"])
        except:
            return JsonResponse(
                {"status": "error", "message": "Could not parse volume"}, status=400
            )

        # create child lot
        rounded_volume = round(volume, 2)
        lot = stock.get_parent_lot()
        lot.pk = None
        lot.transport_document_reference = None
        lot.carbure_client = None
        lot.unknown_client = None
        lot.carbure_delivery_site = None
        lot.unknown_delivery_site = None
        lot.delivery_site_country = None
        lot.lot_status = CarbureLot.DRAFT
        lot.delivery_type = CarbureLot.UNKNOWN
        lot.volume = rounded_volume
        lot.biofuel = stock.biofuel
        lot.weight = lot.get_weight()
        lot.lhv_amount = lot.get_lhv_amount()
        lot.parent_stock = stock
        lot.parent_lot = None
        # common, mandatory data
        lot.delivery_date = try_get_date(entry["delivery_date"])
        lot.year = lot.delivery_date.year
        lot.period = lot.delivery_date.year * 100 + lot.delivery_date.month
        lot.carbure_dispatch_site = stock.depot
        lot.dispatch_site_country = (
            lot.carbure_dispatch_site.country if lot.carbure_dispatch_site else None
        )
        lot.carbure_supplier_id = entity_id
        lot.supplier_certificate = entry.get(
            "supplier_certificate", entity.default_certificate
        )
        lot.added_by_id = entity_id
        lot.dispatch_date = entry.get("dispatch_date", None)
        lot.unknown_client = entry.get("unknown_client", None)
        lot.unknown_delivery_site = entry.get("unknown_delivery_site", None)
        country_code = entry.get("delivery_site_country_id", None)
        if country_code is not None:
            try:
                lot.delivery_site_country = Pays.objects.get(code_pays=country_code)
            except:
                lot.delivery_site_country = None
        lot.transport_document_type = entry.get(
            "transport_document_type", CarbureLot.OTHER
        )
        lot.delivery_type = entry.get("delivery_type", CarbureLot.UNKNOWN)
        lot.transport_document_reference = entry.get(
            "transport_document_reference", lot.delivery_type
        )
        delivery_site_id = entry.get("carbure_delivery_site_id", None)
        try:
            delivery_site = Depot.objects.get(depot_id=delivery_site_id)
            lot.carbure_delivery_site = delivery_site
            lot.delivery_site_country = delivery_site.country
        except:
            pass
        try:
            lot.carbure_client = Entity.objects.get(
                id=entry.get("carbure_client_id", None)
            )
        except:
            lot.carbure_client = None
        if lot.delivery_type in [
            CarbureLot.BLENDING,
            CarbureLot.DIRECT,
            CarbureLot.PROCESSING,
        ]:
            if lot.transport_document_reference is None:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Missing transport_document_reference",
                    },
                    status=400,
                )
            if lot.carbure_client is None:
                return JsonResponse(
                    {"status": "error", "message": "Mandatory carbure_client_id"},
                    status=400,
                )
            if lot.carbure_delivery_site is None:
                return JsonResponse(
                    {"status": "error", "message": "Mandatory carbure_delivery_site"},
                    status=400,
                )
        else:
            if lot.delivery_site_country is None:
                return JsonResponse(
                    {"status": "error", "message": "Mandatory delivery_site_country"},
                    status=400,
                )

        # check if the stock has enough volume and update it
        if rounded_volume > stock.remaining_volume:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Not enough stock available Available [%.2f] Requested [%.2f]"
                    % (stock.remaining_volume, rounded_volume),
                },
                status=400,
            )

        lot.save()
        new_lots.append(lot)
        stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
        stock.remaining_weight = stock.get_weight()
        stock.remaining_lhv_amount = stock.get_lhv_amount()
        stock.save()
        event = CarbureStockEvent()
        event.event_type = CarbureStockEvent.SPLIT
        event.stock = stock
        event.user = request.user
        event.metadata = {"message": "Envoi lot.", "volume_to_deduct": lot.volume}
        event.save()
        # create events
        e = CarbureLotEvent()
        e.event_type = CarbureLotEvent.CREATED
        e.lot = lot
        e.user = request.user
        e.save()
    background_bulk_sanity_checks(new_lots, prefetched_data)
    background_bulk_scoring(new_lots, prefetched_data)
    return JsonResponse({"status": "success", "data": [l.id for l in new_lots]})
