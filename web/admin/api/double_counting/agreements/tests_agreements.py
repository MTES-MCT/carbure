# test with : python web/manage.py test admin.api.double_counting.agreements.tests_agreements.AdminDoubleCountAgreementsTest --keepdb
from datetime import date
from email.mime import application

from core.tests_utils import setup_current_user
from core.models import CarbureLot, Entity, MatierePremiere, Pays, UserRights
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from doublecount.factories.agreement import DoubleCountingRegistrationFactory
from doublecount.factories.application import DoubleCountingApplicationFactory
from doublecount.factories.production import DoubleCountingProductionFactory
from doublecount.factories.sourcing import DoubleCountingSourcingFactory
from doublecount.models import DoubleCountingApplication

from producers.models import ProductionSite
from transactions.factories.carbure_lot import CarbureLotFactory


class Endpoint:
    change_user_role = reverse("entity-users-change-role")


User = get_user_model()


class AdminDoubleCountAgreementsTest(TestCase):
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
        self.production_site.address = "1 rue de la Paix"
        france, _ = Pays.objects.update_or_create(code_pays="FR", name="France")
        self.production_site.country = france
        self.production_site.city = "Paris"
        self.production_site.postal_code = "75000"
        self.production_site.save()
        self.requested_start_year = 2023

    def create_agreement(self):
        app = DoubleCountingApplicationFactory.create(
            producer=self.production_site.producer,
            production_site=self.production_site,
            period_start__year=self.requested_start_year,
            status=DoubleCountingApplication.PENDING,
    )
        sourcing1 = DoubleCountingSourcingFactory.create(dca=app, year=self.requested_start_year)
        sourcing2 = DoubleCountingSourcingFactory.create(dca=app, year=self.requested_start_year)
        production1 = DoubleCountingProductionFactory.create(
            dca=app, feedstock=sourcing2.feedstock, year=self.requested_start_year , approved_quota=1000
        )
        production2 = DoubleCountingProductionFactory.create(
            dca=app, feedstock=sourcing2.feedstock, year=self.requested_start_year + 1, approved_quota=-1
        )
        agreement = DoubleCountingRegistrationFactory.create(
            production_site=self.production_site, 
            valid_from=date(self.requested_start_year, 1, 1),
            application=app,
        )
    
        return agreement

    def test_get_agreements(self):
        agreement1 = self.create_agreement()
        self.create_agreement()

        response = self.client.get(reverse("admin-double-counting-agreements"), {"entity_id": self.admin.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        active_agreements = data["active"]
        self.assertEqual(active_agreements[0]["certificate_id"], agreement1.certificate_id)
        self.assertEqual(len(active_agreements), 2)

    def test_export_agreements(self):
        self.create_agreement()

        # test that the response is an excel file
        response = self.client.get(
            reverse("admin-double-counting-agreements"), {"entity_id": self.admin.id, "as_excel_file": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # def test_get_agreement_details(self):
    #     agreement = self.create_agreement()
    #     agreement_id = agreement.id

    #     feedstocks = MatierePremiere.objects.filter(is_double_compte=True)[:5]

    #     for feedstock in feedstocks:
    #         CarbureLotFactory.create(
    #             feedstock=feedstock,
    #             lot_status=CarbureLot.ACCEPTED,
    #             year=agreement.valid_from.year,
    #             production_site_double_counting_certificate=agreement.certificate_id,
    #             carbure_production_site=self.production_site,
    #         )

    #     response = self.client.get(
    #         reverse("admin-double-counting-agreements-details"),
    #         {"entity_id": self.admin.id, "agreement_id": agreement_id},
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     data = response.json()["data"]

    #     self.assertEqual(data["id"], agreement.id)
