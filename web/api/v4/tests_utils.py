import random
from django.contrib.auth import get_user_model
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice

from producers.models import ProductionSite
from core.models import Depot, Entity, UserRights, UserRightsRequests


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


def setup_current_user(test, email, name, password, entity_rights=[]):
    User = get_user_model()
    user = User.objects.create_user(email=email, name=name, password=password)
    loggedin = test.client.login(username=user.email, password=password)
    test.assertTrue(loggedin)

    for entity, role in entity_rights:
        UserRights.objects.update_or_create(entity=entity, user=user, role=role)
        UserRightsRequests.objects.update_or_create(entity=entity, user=user, role=role)

    response = test.client.post(reverse("api-v4-request-otp"))
    test.assertEqual(response.status_code, 200)
    device, _ = EmailDevice.objects.get_or_create(user=user)
    response = test.client.post(
        reverse("api-v4-verify-otp"), {"otp_token": device.token}
    )
    test.assertEqual(response.status_code, 200)

    return user
