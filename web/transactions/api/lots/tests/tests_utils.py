import random

from core.models import Entity
from transactions.models import Depot, ProductionSite


def get_lot(entity):
    psites = ProductionSite.objects.filter(created_by=entity)
    depots = Depot.objects.filter(country__code_pays="FR")
    clients = Entity.objects.filter(entity_type__in=[Entity.OPERATOR])

    psite = random.choice(psites)
    depot = random.choice(depots)
    client = random.choice(clients)
    data = {
        "entity_id": entity.id,
        "free_field": "unit test",
        "carbure_production_site": psite.name,
        "carbure_producer_id": psite.created_by.id,
        "biofuel_code": "ETH",
        "feedstock_code": "BETTERAVE",
        "country_code": "FR",
        "volume": 34500,
        "eec": 1.0,
        "el": 1.0,
        "ep": 1.0,
        "etd": 1.0,
        "eu": 1.0,
        "transport_document_reference": "DAETEST",
        "carbure_delivery_site_depot_id": depot.depot_id,
        "carbure_client_id": client.id,
        "delivery_date": "13/11/2021",
    }
    return data


def lot_to_form_data(lot, entity, **overrides):
    data = {
        "entity_id": entity.id,
        "lot_id": lot.id,
        "biofuel_code": lot.biofuel.code if lot.biofuel else None,
        "feedstock_code": lot.feedstock.code if lot.feedstock else None,
        "country_code": lot.country_of_origin.code_pays if lot.country_of_origin else None,
        "carbure_producer_id": lot.carbure_producer.id if lot.carbure_producer else None,
        "carbure_supplier_id": lot.carbure_supplier.id if lot.carbure_supplier else None,
        "carbure_client_id": lot.carbure_client.id if lot.carbure_client else None,
        "carbure_delivery_site_depot_id": lot.carbure_delivery_site.depot_id if lot.carbure_delivery_site else None,
        "delivery_date": lot.delivery_date.strftime("%Y-%m-%d") if lot.delivery_date else None,
        "volume": lot.volume,
        "free_field": lot.free_field,
        "carbure_production_site": lot.carbure_production_site.name if lot.carbure_production_site else None,
        "eec": lot.eec if lot.eec else 1.0,
        "el": lot.el if lot.el else 1.0,
        "ep": lot.ep if lot.ep else 1.0,
        "etd": lot.etd if lot.etd else 1.0,
        "eu": lot.eu if lot.eu else 1.0,
        "esca": lot.esca if lot.esca else 1.0,
        "eccs": lot.eccs if lot.eccs else 1.0,
        "eccr": lot.eccr if lot.eccr else 1.0,
        "eee": lot.eee if lot.eee else 1.0,
        "transport_document_reference": lot.transport_document_reference if lot.transport_document_reference else None,
    }
    data.update(overrides)

    # Remove keys with None values
    return {k: v for k, v in data.items() if v is not None}
