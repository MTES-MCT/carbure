import argparse
import os

import django
from django.core.paginator import Paginator
from django.db.models import Q
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, Depot, Entity  # noqa: E402
from core.utils import normalize_string  # noqa: E402
from producers.models import ProductionSite  # noqa: E402


# bruteforcey script that compares all the unknown lot fields with known objects of the database
def fix_entity_name_accent_mismatch(year, batch=1000):
    entities = {normalize_string(entity.name): entity for entity in Entity.objects.all()}
    normalized_entities = entities.keys()

    production_sites = {normalize_string(psite.name): psite for psite in ProductionSite.objects.all()}
    normalized_psites = production_sites.keys()

    depots = {normalize_string(depot.name): depot for depot in Depot.objects.exclude(name="Anonymisé")}
    normalized_depots = depots.keys()

    lots_with_unknown = CarbureLot.objects.filter(year=year).exclude(
        Q(unknown_producer="", unknown_producer__isnull=True)
        | Q(unknown_supplier="", unknown_supplier__isnull=True)
        | Q(unknown_client="", unknown_client__isnull=True)
        | Q(unknown_production_site="", unknown_production_site__isnull=True)
        | Q(unknown_delivery_site="", unknown_delivery_site__isnull=True)
    )

    paginator = Paginator(lots_with_unknown, batch)

    lots_with_known_producer = {}
    lots_with_known_supplier = {}
    lots_with_known_client = {}
    lots_with_known_psite = {}
    lots_with_known_depot = {}

    for page_number in tqdm(paginator.page_range):
        page = paginator.page(page_number)

        for lot in page.object_list:
            normalized_producer = normalize_string(lot.unknown_producer)
            if normalized_producer in normalized_entities:
                lots_with_known_producer[normalized_producer] = lots_with_known_producer.get(normalized_producer, [])
                lots_with_known_producer[normalized_producer].append(lot)

            normalized_supplier = normalize_string(lot.unknown_supplier)
            if normalized_supplier in normalized_entities:
                lots_with_known_supplier[normalized_supplier] = lots_with_known_supplier.get(normalized_supplier, [])
                lots_with_known_supplier[normalized_supplier].append(lot)

            normalized_client = normalize_string(lot.unknown_client)
            if normalized_client in normalized_entities:
                lots_with_known_client[normalized_client] = lots_with_known_client.get(normalized_client, [])
                lots_with_known_client[normalized_client].append(lot)

            normalized_psite = normalize_string(lot.unknown_production_site)
            if normalized_psite in normalized_psites:
                lots_with_known_psite[normalized_psite] = lots_with_known_psite.get(normalized_psite, [])
                lots_with_known_psite[normalized_psite].append(lot)

            normalized_depot = normalize_string(lot.unknown_delivery_site)
            if normalized_depot in normalized_depots:
                lots_with_known_depot[normalized_depot] = lots_with_known_depot.get(normalized_depot, [])
                lots_with_known_depot[normalized_depot].append(lot)

    for producer in lots_with_known_producer:
        carbure_producer = entities.get(producer)
        lots = lots_with_known_producer[producer]
        lot_ids = [lot.id for lot in lots]
        print("Producer lots of %s: %d" % (carbure_producer.name, len(lots)))
        CarbureLot.objects.filter(id__in=lot_ids).update(carbure_producer_id=carbure_producer.id, unknown_producer=None)

    for supplier in lots_with_known_supplier:
        carbure_supplier = entities.get(supplier)
        lots = lots_with_known_supplier[supplier]
        lot_ids = [lot.id for lot in lots]
        print("Supplier lots of %s: %d" % (carbure_supplier.name, len(lots)))
        CarbureLot.objects.filter(id__in=lot_ids).update(carbure_supplier_id=carbure_supplier.id, unknown_supplier=None)

    for client in lots_with_known_client:
        carbure_client = entities.get(client)
        lots = lots_with_known_client[client]
        lot_ids = [lot.id for lot in lots]
        print("Client lots of %s: %d" % (carbure_client.name, len(lots)))
        CarbureLot.objects.filter(id__in=lot_ids).update(carbure_client_id=carbure_client.id, unknown_client=None)

    for psite in lots_with_known_psite:
        production_site = production_sites.get(psite)
        lots = lots_with_known_psite[psite]
        lot_ids = [lot.id for lot in lots]
        print("Production site lots of %s: %d" % (production_site.name, len(lots)))
        CarbureLot.objects.filter(id__in=lot_ids).update(
            carbure_production_site_id=production_site.id, unknown_production_site=None
        )

    for depot_name in lots_with_known_depot:
        depot = depots.get(depot_name)
        lots = lots_with_known_depot[depot_name]
        lot_ids = [lot.id for lot in lots]
        print("Depot lots of %s: %d" % (depot.name, len(lots)))
        CarbureLot.objects.filter(id__in=lot_ids).update(carbure_delivery_site_id=depot.id, unknown_delivery_site=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load ISCC certificates in database")
    parser.add_argument("--year", dest="year", action="store", default=None, help="Which year to focus on")
    parser.add_argument("--batch", dest="batch", action="store", default=1000, help="Which year to focus on")
    args = parser.parse_args()
    fix_entity_name_accent_mismatch(args.year, args.batch)
