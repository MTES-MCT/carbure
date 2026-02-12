import datetime

from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, Entity, MatierePremiere, Pays
from core.tests_utils import setup_current_user
from transactions.models import Site


class ResourcesTest(TestCase):
    fixtures = [
        "json/countries.json",
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
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 4
        # check if querying works
        response = self.client.get(reverse(url) + "?query=bl")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1

    def test_get_feedstocks_is_methanogenic(self):
        # create matieres premieres with is_methanogenic flag
        MatierePremiere.objects.update_or_create(name="Lisier bovin", code="LISIER", defaults={"is_methanogenic": True})
        MatierePremiere.objects.update_or_create(name="Colza", code="COLZA", defaults={"is_methanogenic": False})
        MatierePremiere.objects.update_or_create(name="Fumier", code="FUMIER", defaults={"is_methanogenic": True})

        url = "resources-feedstocks"
        # test filtering by is_methanogenic=true
        response = self.client.get(reverse(url) + "?is_methanogenic=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(item["code"] in ["LISIER", "FUMIER"] for item in data)

        # test filtering by is_methanogenic=false
        response = self.client.get(reverse(url) + "?is_methanogenic=false")
        assert response.status_code == 200
        data = response.json()
        assert any(item["code"] == "COLZA" for item in data)

    def test_get_feedstocks_is_biofuel_feedstock(self):
        # create matieres premieres with is_biofuel_feedstock flag
        MatierePremiere.objects.update_or_create(name="Betterave", code="BETTERAVE", defaults={"is_biofuel_feedstock": True})
        MatierePremiere.objects.update_or_create(
            name="Dechets organiques", code="DECHETS", defaults={"is_biofuel_feedstock": False}
        )
        MatierePremiere.objects.update_or_create(name="Tournesol", code="TOURNESOL", defaults={"is_biofuel_feedstock": True})

        url = "resources-feedstocks"
        # test filtering by is_biofuel_feedstock=true
        response = self.client.get(reverse(url) + "?is_biofuel_feedstock=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(item["code"] in ["BETTERAVE", "TOURNESOL"] for item in data)

        # test filtering by is_biofuel_feedstock=false
        response = self.client.get(reverse(url) + "?is_biofuel_feedstock=false")
        assert response.status_code == 200
        data = response.json()
        assert any(item["code"] == "DECHETS" for item in data)

    def test_get_bcs(self):
        # create biocarburants
        Biocarburant.objects.update_or_create(name="BC1", code="BC1")
        Biocarburant.objects.update_or_create(name="BC2", code="BC2")
        Biocarburant.objects.update_or_create(name="BC3", code="BC3")
        Biocarburant.objects.update_or_create(name="Ethanol", code="ETH")

        url = "resources-biofuels"
        response = self.client.get(reverse(url))
        # api works
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 4
        # check if querying works
        response = self.client.get(reverse(url) + "?query=anol")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()

        assert len(data) == 1

    def test_get_countries(self):
        # create countries
        Pays.objects.update_or_create(name="Honduras", code_pays="HONDA")
        Pays.objects.update_or_create(name="Voituristan", code_pays="VTN")
        Pays.objects.update_or_create(name="Rose Island", code_pays="RS")
        Pays.objects.update_or_create(name="Catalogne", code_pays="CAT")

        url = "resources-countries"
        response = self.client.get(reverse(url))
        # api works
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 4
        # check if querying works
        response = self.client.get(reverse(url) + "?query=isl")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1

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
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 4
        # check if querying works
        response = self.client.get(reverse(url) + "?query=Prod1")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1

    def test_get_producers(self):
        # create entities
        Entity.objects.update_or_create(name="Prod1", entity_type="Producteur")
        Entity.objects.update_or_create(name="Prod2", entity_type="Producteur")
        Entity.objects.update_or_create(name="op1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="tr1", entity_type="Trader")
        Entity.objects.update_or_create(name="adm1", entity_type="Administration")

        url = "resources-entities"
        filter = "?entity_id=Producteur"
        response = self.client.get(reverse(url) + filter)
        # api works
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 2
        # check if querying works
        response = self.client.get(reverse(url) + filter + "&query=od2")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1

    def test_get_operators(self):
        # create entities
        Entity.objects.update_or_create(name="Prod1", entity_type="Producteur")
        Entity.objects.update_or_create(name="Prod2", entity_type="Producteur")
        Entity.objects.update_or_create(name="op1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="op2", entity_type="Opérateur")
        Entity.objects.update_or_create(name="tr1", entity_type="Trader")
        Entity.objects.update_or_create(name="adm1", entity_type="Administration")

        url = "resources-entities"
        filter = "?entity_type=Opérateur"
        response = self.client.get(reverse(url) + filter)
        # api works
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 2
        # check if querying works
        response = self.client.get(reverse(url) + filter + "&query=op2")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1

    def test_get_traders(self):
        # create entities
        Entity.objects.update_or_create(name="Prod1", entity_type="Producteur")
        Entity.objects.update_or_create(name="Prod2", entity_type="Producteur")
        Entity.objects.update_or_create(name="op1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="op2", entity_type="Opérateur")
        Entity.objects.update_or_create(name="tr1", entity_type="Trader")
        Entity.objects.update_or_create(name="tr2", entity_type="Trader")
        Entity.objects.update_or_create(name="adm1", entity_type="Administration")

        url = "resources-entities"
        filter = "?entity_id=Trader"
        response = self.client.get(reverse(url) + filter)
        # api works
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 2
        # check if querying works
        response = self.client.get(reverse(url) + filter + "&query=tr1")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1

    def test_get_delivery_sites(self):
        # create delivery sites
        fr, _ = Pays.objects.update_or_create(name="France", code_pays="FR")
        Site.objects.update_or_create(site_type=Site.BIOFUELDEPOT, name="Depot1", customs_id="007", country=fr)
        Site.objects.update_or_create(site_type=Site.BIOFUELDEPOT, name="Gennevilliers", customs_id="042", country=fr)
        Site.objects.update_or_create(site_type=Site.BIOFUELDEPOT, name="Gennevilliers 2", customs_id="043", country=fr)
        Site.objects.update_or_create(site_type=Site.BIOFUELDEPOT, name="Carcassonne", customs_id="044", country=fr)

        url = "resources-depots"
        response = self.client.get(reverse(url))
        # api works
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 2
        # check if querying works
        response = self.client.get(reverse(url) + "?query=carca")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1

    def test_get_production_sites(self):
        # create production sites
        producer, _ = Entity.objects.update_or_create(name="toto", entity_type="Producteur")
        other_producer, _ = Entity.objects.update_or_create(name="tata", entity_type="Producteur")
        fr, _ = Pays.objects.update_or_create(name="France", code_pays="FR")
        today = datetime.date.today()
        Site.objects.update_or_create(
            site_type=Site.PRODUCTION_BIOLIQUID,
            name="Usine1",
            created_by_id=producer.id,
            country=fr,
            date_mise_en_service=today,
        )
        Site.objects.update_or_create(
            site_type=Site.PRODUCTION_BIOLIQUID,
            name="Usine2",
            created_by_id=producer.id,
            country=fr,
            date_mise_en_service=today,
        )
        Site.objects.update_or_create(
            site_type=Site.PRODUCTION_BIOLIQUID,
            name="Usine3",
            created_by_id=producer.id,
            country=fr,
            date_mise_en_service=today,
        )
        Site.objects.update_or_create(
            site_type=Site.PRODUCTION_BIOLIQUID,
            name="Usine4",
            created_by_id=other_producer.id,
            country=fr,
            date_mise_en_service=today,
        )

        url = "resources-production-sites"
        response = self.client.get(reverse(url))
        # api works
        assert response.status_code == 200
        # and returns 4 entries
        assert len(response.json()) >= 2
        # check if querying works
        response = self.client.get(reverse(url) + "?query=ne3")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 1
        # check if filtering by producer works
        response = self.client.get(reverse(url) + f"?producer_id={producer.id}")
        assert response.status_code == 200
        # and returns filtered data
        data = response.json()
        assert len(data) == 3
