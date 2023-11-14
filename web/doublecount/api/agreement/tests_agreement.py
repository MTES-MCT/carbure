# test with : python web/manage.py test doublecount.api.agreement.tests_agreement.DoubleCountAgreementTest --keepdb
from math import prod
import os
from core.tests_utils import setup_current_user
from core.models import Entity, UserRights
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from doublecount.errors import DoubleCountingError
from doublecount.factories.application import DoubleCountingApplicationFactory
from doublecount.models import DoubleCountingApplication
from producers.models import ProductionSite


User = get_user_model()


class DoubleCountAgreementTest(TestCase):
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

        self.producer, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user, entity=self.producer, defaults={"role": UserRights.ADMIN})
        self.production_site = ProductionSite.objects.first()
        self.requested_start_year = 2023

    def test_get_agreements_status(self):
        ### Setup

        # an application  with status pending  => En attente
        DoubleCountingApplicationFactory.create(
            producer=self.production_site.producer,
            production_site=self.production_site,
            period_start__year=self.requested_start_year,
            status=DoubleCountingApplication.PENDING,
        )

        # an application with status rejected (same year and production site) => ne doit pas etre affichée (will delete the first one)

        # an agreement with status valid => Validé
        # an agreement to renew but already renewed => "Validé"

        # an application with status rejected => Rejeté

        # an agreement to renew => A renouveler

        # an agreement expired => Expiré

        response = self.client.post(
            reverse("doublecount-agreements"),
            {
                "entity_id": self.producer.id,
            },
        )

        data = response.json()["data"]

    def test_get_agreements_quotas(self):
        # check quotas
        print("TODO")

    def test_get_agreement_details_and_quotas(self):
        # pending application without agreement
        # agreement without application and quotas
        print("TODO")
