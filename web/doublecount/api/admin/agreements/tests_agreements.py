# test with : python web/manage.py test admin.api.double_counting.agreements.tests_agreements.AdminDoubleCountAgreementsTest.test_get_agreement_details --keepdb  # noqa: E501
from datetime import date

from django.test import TestCase
from django.urls import reverse

from core.models import CarbureLot, Entity, Pays, UserRights
from core.tests_utils import setup_current_user
from doublecount.factories.agreement import DoubleCountingRegistrationFactory
from doublecount.factories.application import DoubleCountingApplicationFactory
from doublecount.factories.production import DoubleCountingProductionFactory
from doublecount.factories.sourcing import DoubleCountingSourcingFactory
from doublecount.models import DoubleCountingApplication
from transactions.factories.carbure_lot import CarbureLotFactory
from transactions.models import ProductionSite


class AdminDoubleCountAgreementsTest(TestCase):
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

        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)

        self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).first()
        UserRights.objects.update_or_create(user=self.user, entity=self.producer, defaults={"role": UserRights.ADMIN})

        self.production_site = ProductionSite.objects.first()
        self.production_site.address = "1 rue de la Paix"
        france, _ = Pays.objects.update_or_create(code_pays="FR", name="France")
        self.production_site.country = france
        self.production_site.city = "Paris"
        self.production_site.postal_code = "75000"
        self.production_site.save()
        self.requested_start_year = 2023

    def create_agreement(self, status=DoubleCountingApplication.ACCEPTED):
        app = DoubleCountingApplicationFactory.create(
            producer=self.production_site.producer,
            production_site=self.production_site,
            period_start__year=self.requested_start_year,
            status=status,
        )
        sourcing1 = DoubleCountingSourcingFactory.create(dca=app, year=self.requested_start_year)
        sourcing2 = DoubleCountingSourcingFactory.create(dca=app, year=self.requested_start_year)
        sourcing3 = DoubleCountingSourcingFactory.create(dca=app, year=self.requested_start_year)

        prod1 = DoubleCountingProductionFactory.create(
            dca=app, feedstock=sourcing1.feedstock, year=self.requested_start_year, approved_quota=20
        )
        prod2 = DoubleCountingProductionFactory.create(
            dca=app, feedstock=sourcing2.feedstock, year=self.requested_start_year + 1, approved_quota=-1
        )
        prod3 = DoubleCountingProductionFactory.create(  # YEAR
            dca=app, feedstock=sourcing3.feedstock, year=self.requested_start_year, approved_quota=30
        )
        agreement = DoubleCountingRegistrationFactory.create(
            production_site=self.production_site,
            valid_from=date(self.requested_start_year, 1, 1),
            application=app,
            certificate_id=app.certificate_id,
        )

        return agreement, app, prod1, prod2, prod3

    def create_lots(self, agreement, production1, production2, production3):
        start_year = agreement.valid_from.year

        def createLot(production, year, delivery_type=CarbureLot.BLENDING) -> CarbureLot:
            return CarbureLotFactory.create(
                feedstock=production.feedstock,
                biofuel=production.biofuel,
                lot_status=CarbureLot.ACCEPTED,
                delivery_type=delivery_type,
                year=year,
                production_site_double_counting_certificate=agreement.certificate_id,
                carbure_production_site=self.production_site,
                carbure_producer=self.production_site.producer,
            )

        # production 1 (2 lots en 2023 et 1 lot en 2024)
        lot1 = createLot(production1, start_year)
        lot2 = createLot(production1, start_year)
        lot3 = createLot(production1, start_year, delivery_type=CarbureLot.STOCK)

        createLot(production1, start_year + 1)
        createLot(production1, start_year - 1)  # not in the agreement period

        # production 2 skipped because quota has not been validated
        createLot(production2, start_year)  # production2 quota has not been validated
        createLot(production2, start_year + 1)  # production2 quota has not been validated
        prod1_tonnes = round((lot1.weight + lot2.weight) / 1000)
        prod1_progression = round(prod1_tonnes / production1.approved_quota, 2)
        # production 3 (1 lot en 2023)
        lot3 = createLot(production3, start_year)
        prod3_progression = round(round(lot3.weight / 1000) / production3.approved_quota, 2)

        return lot1, lot2, prod1_tonnes, prod1_progression, lot3, prod3_progression

    def test_get_agreements(self):
        agreement1, _, production1, production2, production3 = self.create_agreement()
        _, _, _, prod1_progression, _, prod3_progression = self.create_lots(
            agreement1, production1, production2, production3
        )

        self.create_agreement()

        response = self.client.get(reverse("admin-double-counting-agreements"), {"entity_id": self.admin.id, "year": 2023})
        assert response.status_code == 200
        data = response.json()["data"]
        active_agreements = data["active"]
        assert len(active_agreements) == 2

        active_agreement1 = active_agreements[0]
        assert active_agreement1["certificate_id"] == agreement1.certificate_id

        # quotas
        total_progression = (prod3_progression + prod1_progression) / 2
        assert active_agreement1["quotas_progression"] == round(total_progression, 2)

    def test_get_agreements_excel(self):
        self.create_agreement()

        # test that the response is an excel file
        response = self.client.get(
            reverse("admin-double-counting-agreements"), {"entity_id": self.admin.id, "as_excel_file": "true", "year": 2023}
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def test_get_agreement_details(self):
        agreement, app, production1, production2, production3 = self.create_agreement()
        agreement_id = agreement.id

        start_year = agreement.valid_from.year

        _, lot2, prod1_tonnes, prod1_progression, lot3, _ = self.create_lots(
            agreement, production1, production2, production3
        )

        response = self.client.get(
            reverse("admin-double-counting-agreements-details"),
            {"entity_id": self.admin.id, "agreement_id": agreement_id},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        application = data["application"]
        quotas = data["quotas"]
        assert not data["has_dechets_industriels"]

        assert application["id"] == app.id
        assert len(quotas) == 2  # production 1 +production 3

        quota_line_1 = quotas[0]
        assert quota_line_1["year"] == start_year
        assert quota_line_1["feedstock"]["name"] == lot2.feedstock.name
        assert quota_line_1["production_tonnes"] == round(prod1_tonnes)
        assert quota_line_1["lot_count"] == 2  # 2 lots created in create_lots()
        assert quota_line_1["quotas_progression"] == round(prod1_progression, 2)

        quota_line_2 = quotas[1]
        assert quota_line_2["production_tonnes"] == round(lot3.weight / 1000)
        # without
        agreement.application = None
        agreement.save()
        response = self.client.get(
            reverse("admin-double-counting-agreements-details"),
            {"entity_id": self.admin.id, "agreement_id": agreement_id},
        )
        assert response.status_code == 200
        data = response.json()["data"]

        assert data["application"] is None
        assert data["quotas"] is None
        assert not data["has_dechets_industriels"]
