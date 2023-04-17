import datetime

from api.v4.tests_utils import setup_current_user
from core.models import Biocarburant, Depot, Entity, MatierePremiere, Pays, ProductionSite
from django.test import TestCase
from django.urls import reverse


class ResourcesTest(TestCase):
    fixtures = [
        "json/entities.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)

    def test_get_mps(self):
        # create matieres premieres
        MatierePremiere.objects.update_or_create(name="MAT1", code="M1")
        MatierePremiere.objects.update_or_create(name="MAT2", code="M2")
        MatierePremiere.objects.update_or_create(name="MAT3", code="M3")
        MatierePremiere.objects.update_or_create(name="BLE", code="BLE")

        url = "resources-feedstocks"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 4)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=bl")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 1)

    def test_get_bcs(self):
        # create biocarburants
        Biocarburant.objects.update_or_create(name="BC1", code="BC1")
        Biocarburant.objects.update_or_create(name="BC2", code="BC2")
        Biocarburant.objects.update_or_create(name="BC3", code="BC3")
        Biocarburant.objects.update_or_create(name="Ethanol", code="ETH")

        url = "resources-biofuels"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 4)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=anol")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]

        self.assertEqual(len(data), 1)

    def test_get_countries(self):
        # create countries
        Pays.objects.update_or_create(name="Honduras", code_pays="HONDA")
        Pays.objects.update_or_create(name="Voituristan", code_pays="VTN")
        Pays.objects.update_or_create(name="Rose Island", code_pays="RS")
        Pays.objects.update_or_create(name="Catalogne", code_pays="CAT")

        url = "resources-countries"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 4)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=isl")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 1)

    def test_get_ges(self):
        pass

    def test_get_entities(self):
        # create entities
        Entity.objects.update_or_create(name="Prod1", entity_type="Producteur")
        Entity.objects.update_or_create(name="op1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="tr1", entity_type="Trader")
        Entity.objects.update_or_create(name="adm1", entity_type="Administration")

        url = "resources-entities"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 4)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=op")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 4)

    def test_get_producers(self):
        # create entities
        Entity.objects.update_or_create(name="Prod1", entity_type="Producteur")
        Entity.objects.update_or_create(name="Prod2", entity_type="Producteur")
        Entity.objects.update_or_create(name="op1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="tr1", entity_type="Trader")
        Entity.objects.update_or_create(name="adm1", entity_type="Administration")

        url = "resources-producers"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 2)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=od2")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 1)

    def test_get_operators(self):
        # create entities
        Entity.objects.update_or_create(name="Prod1", entity_type="Producteur")
        Entity.objects.update_or_create(name="Prod2", entity_type="Producteur")
        Entity.objects.update_or_create(name="op1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="op2", entity_type="Opérateur")
        Entity.objects.update_or_create(name="tr1", entity_type="Trader")
        Entity.objects.update_or_create(name="adm1", entity_type="Administration")

        url = "resources-operators"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 2)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=op2")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 1)

    def test_get_traders(self):
        # create entities
        Entity.objects.update_or_create(name="Prod1", entity_type="Producteur")
        Entity.objects.update_or_create(name="Prod2", entity_type="Producteur")
        Entity.objects.update_or_create(name="op1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="op2", entity_type="Opérateur")
        Entity.objects.update_or_create(name="tr1", entity_type="Trader")
        Entity.objects.update_or_create(name="tr2", entity_type="Trader")
        Entity.objects.update_or_create(name="adm1", entity_type="Administration")

        url = "resources-traders"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 2)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=tr1")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 1)

    def test_get_delivery_sites(self):
        # create delivery sites
        fr, _ = Pays.objects.update_or_create(name="France", code_pays="FR")
        Depot.objects.update_or_create(name="Depot1", depot_id="007", country=fr)
        Depot.objects.update_or_create(name="Gennevilliers", depot_id="042", country=fr)
        Depot.objects.update_or_create(name="Gennevilliers 2", depot_id="043", country=fr)
        Depot.objects.update_or_create(name="Carcassonne", depot_id="044", country=fr)

        url = "resources-depots"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 2)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=carca")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 1)

    def test_get_production_sites(self):
        # create production sites
        producer, _ = Entity.objects.update_or_create(name="toto", entity_type="Producteur")
        fr, _ = Pays.objects.update_or_create(name="France", code_pays="FR")
        today = datetime.date.today()
        ProductionSite.objects.update_or_create(
            name="Usine1", producer_id=producer.id, country=fr, date_mise_en_service=today
        )
        ProductionSite.objects.update_or_create(
            name="Usine2", producer_id=producer.id, country=fr, date_mise_en_service=today
        )
        ProductionSite.objects.update_or_create(
            name="Usine3", producer_id=producer.id, country=fr, date_mise_en_service=today
        )
        ProductionSite.objects.update_or_create(
            name="Usine4", producer_id=producer.id, country=fr, date_mise_en_service=today
        )

        url = "resources-production-sites"
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()["data"]), 2)
        # check if querying works
        response = self.client.get(reverse(url) + "?query=ne3")
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()["data"]
        self.assertEqual(len(data), 1)
