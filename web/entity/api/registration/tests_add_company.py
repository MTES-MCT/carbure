# test with : python web/manage.py test entity.api.registration.tests_add_company.EntityRegistrationAddCompanyTest --keepdb

import datetime

from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, EntityCertificate, GenericCertificate, UserRights, UserRightsRequests
from core.tests_utils import setup_current_user
from entity.helpers import enable_entity


class EntityRegistrationAddCompanyTest(TestCase):
    def setUp(self):
        self.cpo = Entity.objects.create(name="CPO", entity_type=Entity.CPO, has_elec=True)

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
        )

    def test_register_company(self):
        GenericCertificate.objects.create(
            certificate_id="EU-ISCC-Cert-PL123-12345678",
            certificate_type="ISCC",
            valid_from=datetime.date(2020, 1, 1),
            valid_until=datetime.date(2021, 1, 1),
        )
        params = {
            "activity_description": "Du blabla dur la société",
            "certificate_id": "EU-ISCC-Cert-PL123-12345678",
            "certificate_type": "ISCC",
            "entity_type": "Opérateur",
            "name": "Mon entreprise test",
            "legal_name": "Mon entreprise test",
            "registered_address": "1 rue de la paix",
            "registered_city": "Paris",
            "registered_country": "FR",
            "registered_zipcode": "75001",
            "registration_id": "542051180",
            "sustainability_officer": "Officer Test",
            "sustainability_officer_email": "officer@test.com",
            "sustainability_officer_phone_number": "0612345678",
        }

        response = self.client.post(
            reverse("entity-registration-add-company"),
            params,
        )
        # # check new entity created
        assert response.status_code == 200
        entity = Entity.objects.get(legal_name="Mon entreprise test", registration_id="542051180")
        assert entity.registered_address == "1 rue de la paix"

        # check certificate created
        entity_certificate = EntityCertificate.objects.get(
            certificate__certificate_id="EU-ISCC-Cert-PL123-12345678", entity=entity
        )
        assert entity.id == entity_certificate.entity.id
        assert entity.default_certificate == "EU-ISCC-Cert-PL123-12345678"

        # duplicated company name error
        response = self.client.post(
            reverse("entity-registration-add-company"),
            params,
        )
        assert response.status_code == 400
        data = response.json()
        error_code = data["error"]
        assert error_code == "COMPANY_NAME_ALREADY_USED"

        # UserRightRequest created with status PENDING
        right_request = UserRightsRequests.objects.get(user=self.user, entity=entity)
        assert right_request is not None

        # # When entity is enabled
        assert entity.is_enabled is False
        fake_request = HttpRequest()
        fake_request.user = self.user
        enable_entity(entity, fake_request)

        ## right request should be accepted
        right_request.refresh_from_db()
        assert right_request.status == "ACCEPTED"

        ## user rights should be created
        user_right = UserRights.objects.get(entity=entity, user=self.user)
        assert user_right is not None

        ## entity should be enabled
        entity.refresh_from_db()
        assert entity.is_enabled is True
