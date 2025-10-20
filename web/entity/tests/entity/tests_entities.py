from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import assert_object_contains_data, setup_current_user
from transactions.factories.certificate import GenericCertificateFactory

ENTITY_DATA = {
    "name": "Test entity",
    "legal_name": "Test entity",
    "registered_address": "Test",
    "registered_country": "FR",
    "registered_zipcode": "Test",
    "registration_id": "97888",
    "sustainability_officer": "Test",
    "sustainability_officer_email": "Test",
    "sustainability_officer_phone_number": "Test",
    "entity_type": Entity.PRODUCER,
    "activity_description": "Test",
}


class AdminEntitiesTest(TestCase):
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
        self.certificate = GenericCertificateFactory.create()
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)

    def test_get_entities(self):
        response = self.client.get(reverse("entity-list") + f"?entity_id={self.admin.id}", {"entity_id": self.admin.id})
        # api works
        assert response.status_code == 200
        # and returns at least 5 entities
        assert len(response.json()) >= 5

        # check if querying works
        response = self.client.get(
            reverse("entity-list") + f"?entity_id={self.admin.id}", {"q": "prod", "entity_id": self.admin.id}
        )
        # works
        assert response.status_code == 200
        # and returns at least 2 entities
        data = response.json()
        assert len(data) >= 2
        # check if the content is correct
        random_entity = data[0]["entity"]
        assert "entity_type" in random_entity
        assert "name" in random_entity

    def test_get_entities_details(self):
        response = self.client.get(
            reverse("entity-detail", kwargs={"id": self.admin.id}) + f"?entity_id={self.admin.id}",
            {"entity_id": self.admin.id, "company_id": self.admin.id},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MTE - DGEC"

    def test_create_entity_success(self):
        data = {"name": "Test Entity", "entity_type": "Producteur", "has_saf": True, "has_elec": False}

        response = self.client.post(reverse("entity-list") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 201
        assert Entity.objects.filter(name="Test Entity").exists()

    def test_create_entity_duplicate_name(self):
        Entity.objects.create(name="Duplicate Entity", entity_type="Producteur")

        data = {"name": "Duplicate Entity", "entity_type": "Producteur", "has_saf": True, "has_elec": False}

        response = self.client.post(reverse("entity-list") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 400
        assert "name" in response.data

    # When a company is a trader, it must have a certificate
    def test_create_foreign_entity_without_certificate_throw_error(self):
        data = {**ENTITY_DATA, "entity_type": Entity.TRADER}
        response = self.client.post(reverse("api-entity-registration-add-company") + f"?entity_id={self.admin.id}", data)

        assert response.status_code == 400
        assert "certificate_id" in response.data
        assert "certificate_type" in response.data

    def test_create_foreign_entity_with_certificate_success(self):
        data = {
            **ENTITY_DATA,
            "certificate_id": self.certificate.certificate_id,
            "certificate_type": self.certificate.certificate_type,
        }

        self.client.post(reverse("api-entity-registration-add-company") + f"?entity_id={self.admin.id}", data)

        entity = Entity.objects.filter(registration_id=ENTITY_DATA["registration_id"]).first()

        assert_object_contains_data(
            self,
            entity,
            {"default_certificate": self.certificate.certificate_id},
        )

    # Certificate is not saved for cpo, airline or saf trader
    def test_create_foreign_entity_without_certificate_cpo_or_airline(self):
        allowed_entities = [Entity.AIRLINE, Entity.CPO, Entity.SAF_TRADER]

        for entity_type in allowed_entities:
            custom_data = {
                **ENTITY_DATA,
                "name": entity_type,
                "entity_type": entity_type,
                "certificate_id": self.certificate.certificate_id,
                "certificate_type": self.certificate.certificate_type,
            }

            self.client.post(reverse("api-entity-registration-add-company") + f"?entity_id={self.admin.id}", custom_data)
            entity = Entity.objects.filter(name=entity_type).first()

            assert_object_contains_data(
                self,
                entity,
                {"default_certificate": ""},
            )
