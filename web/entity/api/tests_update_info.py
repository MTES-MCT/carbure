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
    ]

    def setUp(self):
        self.entity = Entity.objects.all()[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

    def test_update_entity_info(self):
        query = {
            "entity_id": self.entity.id,
            "legal_name": "Mon entreprise",
            "registration_id": "123456789",
            "sustainability_officer_phone_number": "+33674857463",
            "sustainability_officer": "Paris centre",
            "registered_address": "3 rue de la Boétie",
            "registered_zipcode": "75002",
            "registered_city": "Paris",
            "registered_country_code": "FR",
        }

        response = self.client.post(reverse("entity-update-info"), query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        updated_entity = Entity.objects.all()[0]

        self.assertEqual(updated_entity.legal_name, query["legal_name"])
        self.assertEqual(updated_entity.registration_id, query["registration_id"])
        self.assertEqual(
            updated_entity.sustainability_officer_phone_number,
            query["sustainability_officer_phone_number"],
        )
        self.assertEqual(updated_entity.sustainability_officer, query["sustainability_officer"])
        self.assertEqual(updated_entity.registered_address, query["registered_address"])
        self.assertEqual(updated_entity.registered_zipcode, query["registered_zipcode"])
        self.assertEqual(updated_entity.registered_city, query["registered_city"])
        self.assertEqual(updated_entity.registered_country.code_pays, query["registered_country_code"])
