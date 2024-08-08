from core.tests_utils import setup_current_user
from core.models import Entity, Pays, Depot
from django.test import TestCase
from django.urls import reverse


class EntityDepotsTest(TestCase):
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
        # self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")

    def test_depots(self):
        url_get = "entity-depots"
        url_add = "entity-depots-add"
        url_delete = "entity-depots-delete"
        # get 0
        response = self.client.get(reverse(url_get), {"entity_id": self.admin.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 0)
        # add
        france, _ = Pays.objects.update_or_create(code_pays="FR", name="France")
        depot, _ = Depot.objects.update_or_create(depot_id="TEST", name="toto", city="paris", country=france)
        postdata = {
            "entity_id": self.admin.id,
            "delivery_site_id": depot.depot_id,
            "ownership_type": "OWN",
        }
        response = self.client.post(reverse(url_add), postdata)
        self.assertEqual(response.status_code, 200)
        # get 1
        response = self.client.get(reverse(url_get), {"entity_id": self.admin.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 1)
        # delete #TODO
        # response = self.client.post(
        #     reverse(url_delete), {"entity_id": self.admin.id, "delivery_site_id": depot.depot_id}
        # )
        # self.assertEqual(response.status_code, 200)
        # # get 0
        # response = self.client.get(reverse(url_get), {"entity_id": self.admin.id})
        # self.assertEqual(response.status_code, 200)
        # data = response.json()["data"]
        # self.assertEqual(len(data), 0)

    def test_create_depot_success(self):
        params = {
            "entity_id": self.admin.id,
            "name": "Dépôt de test",
            "city": "Paris",
            "country": 77,
            "depot_type": "BIOFUEL DEPOT",
            "depot_id": "123456789012345",
        }
        url_create = reverse("entity-depot-create")
        res = self.client.post(url_create, params)
        self.assertEqual(res.status_code, 200)
        new_depot = Depot.objects.get(depot_id="123456789012345")
        self.assertIsNotNone(new_depot)
        self.assertEqual(new_depot.name, "Dépôt de test")
        self.assertEqual(new_depot.is_enabled, False)

    def test_create_depot_fail(self):
        params = {
            "entity_id": self.admin.id,
            "name": "Dépôt de test",
            "city": "Paris",
            "country": 77,
            "depot_type": "BIOFUEL DEPOT",
        }
        url_create = reverse("entity-depot-create")
        res = self.client.post(url_create, params)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data["error"], "MALFORMED_PARAMS")
        self.assertIsNotNone(data["data"]["depot_id"])
