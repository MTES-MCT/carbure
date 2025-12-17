from django.test import TestCase
from django.urls import reverse

from core.models import Entity, Pays
from core.tests_utils import setup_current_user
from transactions.models import Depot


class EntityDepotsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)
        self.pays = Pays.objects.filter(code_pays="FR")[0]

    def test_depots(self):
        url_get = "api-entity-depots-list"
        url_add = "api-entity-depots-add"
        # get 0
        response = self.client.get(reverse(url_get), {"entity_id": self.admin.id, "company_id": self.admin.id})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        # add
        france, _ = Pays.objects.update_or_create(code_pays="FR", name="France")
        depot, _ = Depot.objects.update_or_create(customs_id="TEST", name="toto", city="paris", country=france)
        postdata = {
            "entity_id": self.admin.id,
            "delivery_site_id": depot.depot_id,
            "ownership_type": "OWN",
        }
        response = self.client.post(reverse(url_add) + f"?entity_id={self.admin.id}", postdata)
        assert response.status_code == 200
        # get 1
        response = self.client.get(reverse(url_get), {"entity_id": self.admin.id, "company_id": self.admin.id})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
