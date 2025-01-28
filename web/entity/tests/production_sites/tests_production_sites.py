from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import (
    Biocarburant,
    Entity,
    MatierePremiere,
    UserRights,
)
from core.tests_utils import setup_current_user
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.models import ProductionSite


class EntityProductionSiteTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)
        self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity1, defaults={"role": UserRights.ADMIN})

        user_model = get_user_model()
        self.user2 = user_model.objects.create_user(
            email="testuser1@toto.com", name="Le Super Testeur 1", password="totopouet"
        )
        self.entity2, _ = Entity.objects.update_or_create(name="Le Super Operateur 1", entity_type="Opérateur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity2, defaults={"role": UserRights.RW})

    def test_production_sites_settings(self):
        url_get = "api-entity-production-sites-list"
        url_add = "api-entity-production-sites-list"
        url_update = "api-entity-production-sites-update-item"
        url_delete = "api-entity-production-sites-delete"
        url_set_mps = "api-entity-production-sites-set-feedstocks"
        url_set_bcs = "api-entity-production-sites-set-biofuels"

        # get - 0 sites
        response = self.client.get(
            reverse(url_get) + f"?entity_id={self.entity1.id}",
            {"entity_id": self.entity1.id},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        # add 1
        psite = {
            "country_code": "FR",
            "name": "Site prod 1",
            "date_mise_en_service": "2020-12-01",
            "ges_option": "Actual",
            "entity_id": self.entity1.id,
            "eligible_dc": "true",
            "dc_reference": "DC-FR-12-493",
            "site_siret": "FR0001",
            "address": "1 rue de la Paix",
            "city": "Seynod",
            "postal_code": "74600",
            "manager_name": "",
            "manager_phone": "",
            "manager_email": "",
        }
        response = self.client.post(reverse(url_add) + f"?entity_id={self.entity1.id}", psite)
        assert response.status_code == 200
        # check in db
        site = ProductionSite.objects.get(site_siret="FR0001")
        # update
        psite["postal_code"] = "75018"
        response = self.client.post(
            reverse(url_update, kwargs={"id": site.id}) + f"?entity_id={self.entity1.id}",
            psite,
            content_type="application/json",
        )
        assert response.status_code == 200  # update without specifying site_id
        psite["production_site_id"] = site.id
        psite["country_code"] = "WW"
        response = self.client.post(
            reverse(url_update, kwargs={"id": site.id}) + f"?entity_id={self.entity1.id}",
            psite,
            content_type="application/json",
        )
        assert response.status_code == 400  # unknown country code WW
        psite["country_code"] = "FR"
        response = self.client.post(
            reverse(url_update, kwargs={"id": site.id}) + f"?entity_id={self.entity1.id}",
            psite,
            content_type="application/json",
        )
        assert response.status_code == 200
        site = ProductionSite.objects.get(site_siret="FR0001")
        assert site.postal_code == "75018"

        # set mps/bcs
        MatierePremiere.objects.update_or_create(code="COLZA", name="Colza")
        MatierePremiere.objects.update_or_create(code="BEETROOT", name="Betterave")
        Biocarburant.objects.update_or_create(code="ETH", name="Ethanol")
        Biocarburant.objects.update_or_create(code="HVO", name="HVO")

        response = self.client.post(
            reverse(url_set_mps, kwargs={"id": site.id}) + f"?entity_id={self.entity1.id}",
            {
                "entity_id": self.entity1.id,
                "production_site_id": site.id,
                "matiere_premiere_codes": ["COLZA", "BEETROOT"],
            },
        )
        assert response.status_code == 200
        response = self.client.post(
            reverse(url_set_bcs, kwargs={"id": site.id}) + f"?entity_id={self.entity1.id}",
            {
                "entity_id": self.entity1.id,
                "production_site_id": site.id,
                "biocarburant_codes": ["ETH", "HVO"],
            },
        )
        assert response.status_code == 200
        # check
        inputs = ProductionSiteInput.objects.filter(production_site=site)
        outputs = ProductionSiteOutput.objects.filter(production_site=site)
        assert len(inputs) == 2
        assert len(outputs) == 2

        # delete
        post = {"entity_id": self.entity1.id}
        response = self.client.delete(reverse(url_delete, kwargs={"id": site.id + 10}) + f"?entity_id={self.entity1.id}")
        assert response.status_code == 400  # missing production_site_id

        post["production_site_id"] = site.id
        response = self.client.delete(reverse(url_delete, kwargs={"id": site.id}) + f"?entity_id={self.entity1.id}")
        assert response.status_code == 200
        # get - 0 sites
        response = self.client.get(reverse(url_get) + f"?entity_id={self.entity1.id}", {"entity_id": self.entity1.id})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_add_production_site(self):
        # "entity_id": self.entity1.id
        postdata = {}
        url = "api-entity-production-sites-list"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "name" in response.json()
        postdata["name"] = "Site de production 007"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "country_code" in response.json()
        postdata["country_code"] = "zz"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "date_mise_en_service" in response.json()

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "ges_option" in response.json()
        postdata["ges_option"] = "Default"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "site_siret" in response.json()
        postdata["site_siret"] = "FR78895468"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "postal_code" in response.json()
        postdata["postal_code"] = "64430"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "manager_name" in response.json()
        postdata["manager_name"] = "William Rock"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "manager_phone" in response.json()
        postdata["manager_phone"] = "0145247000"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "manager_email" in response.json()
        postdata["manager_email"] = "will.rock@example.com"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "city" in response.json()
        postdata["city"] = "Guermiette"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "address" in response.json()
        postdata["address"] = "1 rue de la paix"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400
        assert "date_mise_en_service" in response.json()
        postdata["date_mise_en_service"] = "2007-05-12"

        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 400

        postdata["country_code"] = "FR"

        # response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        # assert response.status_code == 400
        # assert response.json()["message"] == "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_PRODUCER"
        postdata["entity_id"] = self.entity1.id
        response = self.client.post(reverse(url) + f"?entity_id={self.entity1.id}", postdata)
        assert response.status_code == 200
