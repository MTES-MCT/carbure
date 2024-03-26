# test with : python web/manage.py test entity.api.tests_apply_new_company.EntityApplyNewCompanyTest --keepdb

import datetime

from core.tests_utils import setup_current_user
from core.models import Entity, EntityCertificate, GenericCertificate
from django.test import TestCase
from django.urls import reverse


class EntityApplyNewCompanyTest(TestCase):
    def setUp(self):

        self.cpo = Entity.objects.create(
            name="CPO",
            entity_type=Entity.CPO,
            has_elec=True,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
        )

    def test_apply_new_company(self):
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
            "legal_name": "Mon entreprise test",
            "registered_address": "1 rue de la paix",
            "registered_city": "Paris",
            "registered_country": "France",
            "registered_zipcode": "75001",
            "registration_id": "542051180",
            "sustainability_officer": "Officer Test",
            "sustainability_officer_email": "officer@test.com",
            "sustainability_officer_phone_number": "0612345678",
        }
        response = self.client.post(
            reverse("entity-apply-new-company"),
            params,
        )
        # check new entity created
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(legal_name="Mon entreprise test", registration_id="542051180")
        self.assertEqual(entity.registered_address, "1 rue de la paix")

        # check certificate created
        certificate = EntityCertificate.objects.get(certificate__certificate_id="EU-ISCC-Cert-PL123-12345678", entity=entity)
        self.assertEqual(entity.id, certificate.entity.id)
