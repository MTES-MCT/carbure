# test with : python web/manage.py test doublecount.api.agreements.tests_agreements.DoubleCountAgreementsTest.test_get_agreements --keepdb  # noqa: E501
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Entity, UserRights
from core.tests_utils import setup_current_user
from doublecount.factories.agreement import DoubleCountingRegistrationFactory
from doublecount.factories.application import DoubleCountingApplicationFactory
from doublecount.models import DoubleCountingApplication
from transactions.models import Site as ProductionSite

User = get_user_model()


class DoubleCountAgreementsTest(TestCase):
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
        self.production_site1 = ProductionSite.objects.first()
        self.production_site1.producer = self.producer
        self.production_site1.save()

        self.production_site2 = ProductionSite.objects.first()
        self.production_site2.producer = self.producer
        self.production_site2.save()

        self.requested_start_year = 2023

    def test_get_agreements(self):
        ### Setup
        def create_application(start_year, production_site, status=DoubleCountingApplication.ACCEPTED):
            return DoubleCountingApplicationFactory.create(
                producer=self.producer,
                production_site=production_site,
                period_start__year=start_year,
                period_end__year=start_year + 1,
                status=status,
            )

        # an application  with status pending  => En attente
        create_application(self.requested_start_year + 1, self.production_site1, DoubleCountingApplication.PENDING)

        # an agreement with status valid => Validé
        application = create_application(
            self.requested_start_year - 1, self.production_site1, DoubleCountingApplication.ACCEPTED
        )
        DoubleCountingRegistrationFactory.create(
            production_site=self.production_site1,
            valid_from=date(self.requested_start_year, 1, 1),
            application=application,
            certificate_id=application.certificate_id,
        )
        # an agreement to renew but already renewed => "Validé"

        # an application with status rejected => Rejeté
        create_application(self.requested_start_year + 1, self.production_site2, DoubleCountingApplication.REJECTED)

        # an agreement to renew => A renouveler

        # an agreement expired => Expiré

        response = self.client.post(
            reverse("doublecount-agreements"),
            {
                "entity_id": self.producer.id,
            },
        )

        data = response.json()["data"]

        application1 = data[0]
        application2 = data[1]
        application3 = data[2]
        assert len(data) == 3

        assert application1["quotas_progression"] is None
        assert application2["quotas_progression"] == 0
        assert application3["quotas_progression"] is None

    def test_get_agreements_quotas(self):
        # check quotas
        print("TODO")

    def test_get_agreement_details_and_quotas(self):
        # pending application without agreement
        # agreement without application and quotas
        print("TODO")
