import random

from producers.models import ProductionSite
from core.models import Depot, Entity


def get_lot(entity):
    psites = ProductionSite.objects.filter(producer=entity)
    depots = Depot.objects.filter(country__code_pays="FR")
    clients = Entity.objects.filter(entity_type__in=[Entity.OPERATOR])

    psite = random.choice(psites)
    depot = random.choice(depots)
    client = random.choice(clients)
    data = {
        "entity_id": entity.id,
        "free_field": "unit test",
        "carbure_production_site": psite.name,
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
