from django.urls import reverse

from core.models import Entity, ExternalAdminRights, GenericCertificate, UserRights, UserRightsRequests
from core.tests_utils import setup_current_user
from entity.tests import TestCase

FAKE_COMPANY_DATA = {
    "name": None,
    "entity_type": None,
    "activity_description": "Description of the company's activity",
    "legal_name": "Company Legal Name",
    "registered_address": "123 Example Street",
    "registered_city": "Example City",
    "registered_country_code": "FR",
    "registered_zipcode": "12345",
    "registration_id": "123456789",
    "sustainability_officer": "John Doe",
    "sustainability_officer_email": "johndoe@example.com",
    "sustainability_officer_phone_number": "+1234567890",
    "website": "https://www.example.com",
    "vat_number": "FR123456789",
    "certificate_id": "CERT123456",
    "certificate_type": "ISCC",
}


class EntityEnableSourceTest(TestCase):
    def setUp(self):
        super().setUp()

        GenericCertificate.objects.update_or_create(
            certificate_id="CERT123456",
            certificate_type="ISCC",
            valid_from="2024-01-01",
            valid_until="2124-01-01",
        )

        self.admin = Entity.objects.create(name="Admin entity", entity_type=Entity.ADMIN)
        self.elec_admin = Entity.objects.create(name="Elec Admin entity", entity_type=Entity.EXTERNAL_ADMIN)
        self.saf_admin = Entity.objects.create(name="SAF Admin entity", entity_type=Entity.EXTERNAL_ADMIN)

        ExternalAdminRights.objects.create(entity=self.elec_admin, right=ExternalAdminRights.ELEC)
        ExternalAdminRights.objects.create(entity=self.saf_admin, right=ExternalAdminRights.AIRLINE)

    def test_enable_producer(self):
        producer_user = setup_current_user(self, "user@entity.local", "Entity user", "gogogo", [])

        response = self.client.post(
            reverse("api-entity-registration-add-company"),
            {**FAKE_COMPANY_DATA, "name": "Test Producer", "entity_type": Entity.PRODUCER},
        )

        assert response.status_code == 200

        producer = Entity.objects.get(name="Test Producer")
        rights_requests = UserRightsRequests.objects.get(user=producer_user, entity=producer)

        assert rights_requests.status == "PENDING"

        # 1. try to enable producer with as an elec admin
        setup_current_user(self, "user@elec-admin.local", "Elec admin user", "gogogo", [(self.elec_admin, UserRights.ADMIN)])

        response = self.client.post(
            reverse("entity-admin-enable", kwargs={"id": producer.pk}) + f"?entity_id={self.elec_admin.pk}"
        )
        assert response.status_code == 400

        producer.refresh_from_db()
        rights_requests.refresh_from_db()

        assert producer.is_enabled is False
        assert rights_requests.status == "PENDING"
        assert UserRights.objects.filter(user=producer_user, entity=producer).count() == 0

        # 2. try to enable producer with as a saf admin
        setup_current_user(self, "user@saf-admin.local", "Saf admin user", "gogogo", [(self.saf_admin, UserRights.ADMIN)])

        response = self.client.post(
            reverse("entity-admin-enable", kwargs={"id": producer.pk}) + f"?entity_id={self.saf_admin.pk}"
        )

        assert response.status_code == 400

        producer.refresh_from_db()
        rights_requests.refresh_from_db()

        assert producer.is_enabled is False
        assert rights_requests.status == "PENDING"
        assert UserRights.objects.filter(user=producer_user, entity=producer).count() == 0

        # 3. try to enable producer with as a super admin
        setup_current_user(self, "user@admin.local", "Saf admin user", "gogogo", [(self.admin, UserRights.ADMIN)], True)

        response = self.client.post(
            reverse("entity-admin-enable", kwargs={"id": producer.pk}) + f"?entity_id={self.admin.pk}"
        )

        assert response.status_code == 200

        producer.refresh_from_db()
        rights_requests.refresh_from_db()

        assert producer.is_enabled is True
        assert rights_requests.status == "ACCEPTED"
        assert UserRights.objects.filter(user=producer_user, entity=producer).count() == 1
