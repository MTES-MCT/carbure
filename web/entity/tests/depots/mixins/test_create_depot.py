from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import Entity, Pays
from core.tests_utils import setup_current_user
from transactions.models import Depot


class TestCreateDepot(TestCase):
    fixtures = [
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)
        self.pays = Pays.objects.filter(code_pays="FR")[0]

    @patch("entity.views.depots.mixins.create.get_coordinates")
    def test_create_depot_success(self, mock_get_coordinates):
        mock_get_coordinates.return_value = (48.8566, 2.3522)
        params = {
            "entity_id": self.admin.id,
            "name": "Dépôt de test",
            "city": "Paris",
            "country_code": self.pays.code_pays,
            "depot_type": "BIOFUEL DEPOT",
            "depot_id": "123456789012345",  # keep "depot_id" to not change front api call (but named "customs_id" from now)
            "ownership_type": "OWN",
        }
        url_create = reverse("api-entity-depots-create-depot") + f"?entity_id={self.admin.id}"

        res = self.client.post(url_create, params)

        assert res.status_code == 200
        new_depot = Depot.objects.get(customs_id="123456789012345")
        assert new_depot is not None
        assert new_depot.name == "Dépôt de test"
        assert new_depot.is_enabled is False
        assert new_depot.gps_coordinates == "48.8566,2.3522"

    @patch("entity.views.depots.mixins.create.get_coordinates")
    def test_create_depot_fail(self, mock_get_coordinates):
        mock_get_coordinates.return_value = (48.8566, 2.3522)
        params = {
            "entity_id": self.admin.id,
            "name": "Dépôt de test",
            "city": "Paris",
            "country_code": self.pays.code_pays,
            "depot_type": "BIOFUEL DEPOT",
        }
        url_create = reverse("api-entity-depots-create-depot") + f"?entity_id={self.admin.id}"

        res = self.client.post(url_create, params)

        assert res.status_code == 400
        data = res.json()
        assert data["depot_id"] is not None
