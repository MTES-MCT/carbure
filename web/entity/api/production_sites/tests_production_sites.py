from api.v4.tests_utils import setup_current_user
from core.models import Entity, Pays, ProductionSite, MatierePremiere, Biocarburant, UserRights
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from django.test import TestCase
from django.urls import reverse


class EntityProductionSiteTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)
        self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity1, defaults={"role": UserRights.ADMIN})

    def test_production_sites_settings(self):
        url_get = "entity-production-sites"
        url_add = "entity-production-sites-add"
        url_update = "entity-production-sites-update"
        url_delete = "entity-production-sites-delete"
        url_set_mps = "entity-production-sites-set-feedstocks"
        url_set_bcs = "entity-production-sites-set-biofuels"

        # get - 0 sites
        response = self.client.get(reverse(url_get), {"entity_id": self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 0)
        # add 1
        france, _ = Pays.objects.update_or_create(code_pays="FR", name="France")
        psite = {
            "country_code": "FR",
            "name": "Site prod 1",
            "date_mise_en_service": "2020-12-01",
            "ges_option": "ACTUAL",
            "entity_id": self.entity1.id,
            "eligible_dc": "true",
            "dc_reference": "DC-FR-12-493",
            "site_id": "FR0001",
            "city": "Seynod",
            "postal_code": "74600",
            "manager_name": "",
            "manager_phone": "",
            "manager_email": "",
        }
        response = self.client.post(reverse(url_add), psite)
        self.assertEqual(response.status_code, 200)
        # check in db
        site = ProductionSite.objects.get(site_id="FR0001")
        # update
        psite["postal_code"] = "75018"
        response = self.client.post(reverse(url_update), psite)
        self.assertEqual(response.status_code, 400)  # update without specifying site_id
        psite["production_site_id"] = site.id
        psite["country_code"] = "WW"
        response = self.client.post(reverse(url_update), psite)
        self.assertEqual(response.status_code, 400)  # unknown country code WW
        psite["country_code"] = "FR"
        response = self.client.post(reverse(url_update), psite)
        self.assertEqual(response.status_code, 200)
        site = ProductionSite.objects.get(site_id="FR0001")
        self.assertEqual(site.postal_code, "75018")

        # set mps/bcs
        MatierePremiere.objects.update_or_create(code="COLZA", name="Colza")
        MatierePremiere.objects.update_or_create(code="BEETROOT", name="Betterave")
        Biocarburant.objects.update_or_create(code="ETH", name="Ethanol")
        Biocarburant.objects.update_or_create(code="HVO", name="HVO")

        response = self.client.post(
            reverse(url_set_mps),
            {
                "entity_id": self.entity1.id,
                "production_site_id": site.id,
                "matiere_premiere_codes": ["COLZA", "BEETROOT"],
            },
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse(url_set_bcs),
            {"entity_id": self.entity1.id, "production_site_id": site.id, "biocarburant_codes": ["ETH", "HVO"]},
        )
        self.assertEqual(response.status_code, 200)
        # check
        inputs = ProductionSiteInput.objects.filter(production_site=site)
        outputs = ProductionSiteOutput.objects.filter(production_site=site)
        self.assertEqual(len(inputs), 2)
        self.assertEqual(len(outputs), 2)

        # delete
        post = {"entity_id": self.entity1.id}
        response = self.client.post(reverse(url_delete), post)
        self.assertEqual(response.status_code, 400)  # missing production_site_id

        post["production_site_id"] = site.id
        response = self.client.post(reverse(url_delete), post)
        self.assertEqual(response.status_code, 200)
        # get - 0 sites
        response = self.client.get(reverse(url_get), {"entity_id": self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 0)
