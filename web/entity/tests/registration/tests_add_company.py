# test with : python web/manage.py test entity.api.registration.tests_add_company.EntityRegistrationAddCompanyTest --keepdb

import datetime

from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from rest_framework import serializers
from web.entity.factories.entity import EntityFactory
from web.transactions.factories.certificate import GenericCertificateFactory

from core.models import Entity, EntityCertificate, GenericCertificate, Pays, UserRights, UserRightsRequests
from core.tests_utils import assert_object_contains_data, setup_current_user
from entity.services.enable_entity import enable_entity
from entity.views.registration.add_company import EntityCompanySerializer


class EntityRegistrationAddCompanyTest(TestCase):
    def setUp(self):
        self.country = Pays.objects.create(code_pays="FR", name="France", name_en="France")
        self.cpo = Entity.objects.create(name="CPO", entity_type=Entity.CPO, has_elec=True)

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
        )
        self.certificate = GenericCertificateFactory.create()
        self.entity_data = model_to_dict(EntityFactory.build(entity_type=Entity.PRODUCER))
        self.entity_data["registered_country"] = "FR"
        self.entity_data.pop("id")
        self.entity_data.pop("parent_entity")

    def test_register_company(self):
        GenericCertificate.objects.create(
            certificate_id="EU-ISCC-Cert-PL123-12345678",
            certificate_type="ISCC",
            valid_from=datetime.date(2020, 1, 1),
            valid_until=datetime.date(2021, 1, 1),
        )
        params = {
            **self.entity_data,
            "certificate_id": "EU-ISCC-Cert-PL123-12345678",
            "certificate_type": "ISCC",
        }

        response = self.client.post(
            reverse("api-entity-registration-add-company"),
            params,
        )
        # # check new entity created

        assert response.status_code == 200
        entity = Entity.objects.get(legal_name=params["legal_name"], registration_id=params["registration_id"])
        assert entity.registered_address == params["registered_address"]

        # check certificate created
        entity_certificate = EntityCertificate.objects.get(
            certificate__certificate_id=params["certificate_id"], entity=entity
        )
        assert entity.id == entity_certificate.entity.id
        assert entity.default_certificate == params["certificate_id"]

        # duplicated company name error
        response = self.client.post(
            reverse("api-entity-registration-add-company"),
            self.entity_data,
        )
        assert response.status_code == 400
        data = response.json()
        assert "name" in data

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

    # When a company is a trader, it must have a certificate
    def test_create_foreign_entity_without_certificate_throw_error(self):
        data = {**self.entity_data, "entity_type": Entity.TRADER}
        serializer = EntityCompanySerializer()

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(data)

        errors = context.exception.detail
        self.assertIn("certificate_id", errors)
        self.assertIn("certificate_type", errors)

    # Certificate is not saved for cpo, airline or saf trader
    def test_create_foreign_entity_without_certificate_cpo_or_airline(self):
        allowed_entities = [Entity.AIRLINE, Entity.CPO, Entity.SAF_TRADER]

        for entity_type in allowed_entities:
            custom_data = {
                **self.entity_data,
                "name": entity_type,
                "entity_type": entity_type,
                "certificate_id": self.certificate.certificate_id,
                "certificate_type": self.certificate.certificate_type,
            }

            self.client.post(reverse("api-entity-registration-add-company"), custom_data)

            entity = Entity.objects.filter(name=entity_type).first()

            assert_object_contains_data(
                self,
                entity,
                {"default_certificate": ""},
            )
