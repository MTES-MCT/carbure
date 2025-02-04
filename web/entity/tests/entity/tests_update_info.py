from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user


class SettingUpdateEntityTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.all()[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

    def test_update_entity_info(self):
        query = {
            "entity_id": self.entity.id,
            "legal_name": "Mon entreprise",
            "registration_id": "123456789",
            "sustainability_officer_phone_number": "",
            "sustainability_officer": "",
            "registered_address": "3 rue de la Boétie",
            "registered_zipcode": "75002",
            "registered_city": "Paris",
            "registered_country_code": "FR",
        }

        response = self.client.post(reverse("entity-update-entity-info") + f"?entity_id={self.entity.id}", query)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        updated_entity = Entity.objects.all()[0]

        assert updated_entity.legal_name == query["legal_name"]
        assert updated_entity.registration_id == query["registration_id"]
        assert updated_entity.sustainability_officer_phone_number == query["sustainability_officer_phone_number"]
        assert updated_entity.sustainability_officer == query["sustainability_officer"]
        assert updated_entity.registered_address == query["registered_address"]
        assert updated_entity.registered_zipcode == query["registered_zipcode"]
        assert updated_entity.registered_city == query["registered_city"]
        assert updated_entity.registered_country.code_pays == query["registered_country_code"]
