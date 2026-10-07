# test with : python web/manage.py test admin.api.double_counting.agreements.tests_agreements.AdminDoubleCountAgreementsTest.test_get_agreement_details --keepdb  # noqa: E501
from datetime import date

from django.test import TestCase
from django.urls import reverse

from certificates.models import DoubleCountingRegistration
from core.models import CarbureLot, Entity, MatierePremiere, Pays, UserRights
from core.tests_utils import setup_current_user
from doublecount.errors import DoubleCountingError
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
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.ext_admin = Entity.objects.create(name="ExternalAdminTest", entity_type=Entity.EXTERNAL_ADMIN)

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

        response = self.client.get(
            reverse("double-counting-agreements-agreement-admin"),
            {"entity_id": self.admin.id, "year": 2023, "order_by": "production_site"},
        )
        assert response.status_code == 200
        data = response.json()
        active_agreements = data["active"]
        assert len(active_agreements) == 2

        active_agreement1 = active_agreements[0]
        assert active_agreement1["certificate_id"] == agreement1.certificate_id

        # quotas
        total_progression = (prod3_progression + prod1_progression) / 2
        assert active_agreement1["quotas_progression"] == round(total_progression, 2)

    def test_get_agreements_inactive(self):
        """Test retrieving inactive agreements."""
        valid_agreement, *_ = self.create_agreement()
        suspended_agreement, *_ = self.create_agreement()
        suspended_agreement.status = DoubleCountingRegistration.SUSPENDED
        suspended_agreement.save()

        response = self.client.get(
            reverse("double-counting-agreements-agreement-admin"),
            {"entity_id": self.admin.id, "year": 2023, "order_by": "production_site"},
        )
        assert response.status_code == 200
        data = response.json()

        assert [a["id"] for a in data["active"]] == [valid_agreement.id]
        assert [a["id"] for a in data["inactive"]] == [suspended_agreement.id]
        assert data["inactive"][0]["status"] == DoubleCountingRegistration.SUSPENDED

    def test_get_agreements_incoming_and_expired_exclude_inactive(self):
        valid_agreement, *_ = self.create_agreement()
        suspended_agreement, *_ = self.create_agreement()
        suspended_agreement.status = DoubleCountingRegistration.SUSPENDED
        suspended_agreement.save()

        def get_lists(year):
            response = self.client.get(
                reverse("double-counting-agreements-agreement-admin"),
                {"entity_id": self.admin.id, "year": year},
            )
            assert response.status_code == 200
            return response.json()

        # agreements start in 2023 and end after the current year
        incoming = get_lists(self.requested_start_year - 1)["incoming"]
        assert [a["id"] for a in incoming] == [valid_agreement.id]

        expired = get_lists(valid_agreement.valid_until.year + 1)["expired"]
        assert [a["id"] for a in expired] == [valid_agreement.id]

    def test_update_agreement_status(self):
        agreement, *_ = self.create_agreement()
        response = self.client.patch(
            reverse("double-counting-agreements-update-status", kwargs={"id": agreement.id}),
            {"status": DoubleCountingRegistration.SUSPENDED},
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )

        assert response.status_code == 200
        agreement.refresh_from_db()
        assert agreement.status == DoubleCountingRegistration.SUSPENDED

    def test_update_inactive_agreement_status(self):
        agreement, *_ = self.create_agreement()
        agreement.status = DoubleCountingRegistration.WITHDRAWN
        agreement.save()

        response = self.client.patch(
            reverse("double-counting-agreements-update-status", kwargs={"id": agreement.id}),
            {"status": DoubleCountingRegistration.TERMINATED},
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )

        assert response.status_code == 200
        agreement.refresh_from_db()
        assert agreement.status == DoubleCountingRegistration.TERMINATED

    def test_update_agreement_status_to_valid(self):
        agreement, *_ = self.create_agreement()
        agreement.status = DoubleCountingRegistration.SUSPENDED
        agreement.save()

        response = self.client.patch(
            reverse("double-counting-agreements-update-status", kwargs={"id": agreement.id}),
            {"status": DoubleCountingRegistration.VALID},
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )

        assert response.status_code == 200
        agreement.refresh_from_db()
        assert agreement.status == DoubleCountingRegistration.VALID

    def test_read_only_admin_cannot_update_agreement_status(self):
        agreement, *_ = self.create_agreement()
        setup_current_user(self, "readonly@carbure.local", "Read Only", "gogogo", [(self.admin, UserRights.RO)], True)

        update_response = self.client.patch(
            reverse("double-counting-agreements-update-status", kwargs={"id": agreement.id}),
            {"status": DoubleCountingRegistration.SUSPENDED},
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )
        bulk_response = self.client.post(
            reverse("double-counting-agreements-bulk-update-status"),
            {"agreement_ids": [agreement.id], "status": DoubleCountingRegistration.SUSPENDED},
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )

        assert update_response.status_code == 403
        assert bulk_response.status_code == 403
        agreement.refresh_from_db()
        assert agreement.status == DoubleCountingRegistration.VALID

    def test_bulk_update_agreement_status(self):
        agreements = [self.create_agreement()[0] for _ in range(2)]

        response = self.client.post(
            reverse("double-counting-agreements-bulk-update-status"),
            {
                "agreement_ids": [agreement.id for agreement in agreements],
                "status": DoubleCountingRegistration.SUSPENDED,
            },
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )

        assert response.status_code == 200
        assert response.json()["updated_count"] == len(agreements)
        for agreement in agreements:
            agreement.refresh_from_db()
            assert agreement.status == DoubleCountingRegistration.SUSPENDED

    def test_bulk_update_agreement_status_rejects_inactive_selection(self):
        valid_agreement, *_ = self.create_agreement()
        inactive_agreement, *_ = self.create_agreement()
        inactive_agreement.status = DoubleCountingRegistration.WITHDRAWN
        inactive_agreement.save()

        response = self.client.post(
            reverse("double-counting-agreements-bulk-update-status"),
            {
                "agreement_ids": [valid_agreement.id, inactive_agreement.id],
                "status": DoubleCountingRegistration.TERMINATED,
            },
            content_type="application/json",
            QUERY_STRING=f"entity_id={self.admin.id}",
        )

        assert response.status_code == 400
        assert response.json() == {"message": DoubleCountingError.AGREEMENTS_NOT_UPDATABLE}
        valid_agreement.refresh_from_db()
        assert valid_agreement.status == DoubleCountingRegistration.VALID

    def test_get_agreements_excel(self):
        self.create_agreement()

        # test that the response is an excel file
        response = self.client.get(
            reverse("double-counting-agreements-export"), {"entity_id": self.admin.id, "as_excel_file": "true", "year": 2023}
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def test_get_agreement_details(self):
        agreement, app, production1, production2, production3 = self.create_agreement()
        agreement_id = agreement.id
        non_industrial_feedstocks = list(
            MatierePremiere.biofuel.filter(is_double_compte=True, is_industrial_waste=False).order_by("id")[:3]
        )
        self.assertEqual(len(non_industrial_feedstocks), 3)
        for production, feedstock in zip((production1, production2, production3), non_industrial_feedstocks, strict=True):
            production.feedstock = feedstock
            production.save(update_fields=["feedstock"])

        start_year = agreement.valid_from.year

        lot1, _, prod1_tonnes, prod1_progression, lot3, _ = self.create_lots(
            agreement, production1, production2, production3
        )

        response = self.client.get(
            reverse("double-counting-agreements-detail", kwargs={"id": agreement_id}),
            {"entity_id": self.admin.id, "agreement_id": agreement_id},
        )
        assert response.status_code == 200
        data = response.json()
        application = data["application"]
        quotas = data["quotas"]
        assert data["has_dechets_industriels"] is False

        assert application["id"] == app.id
        assert len(quotas) == 2  # production 1 +production 3

        quota_line_1 = [q for q in quotas if q["feedstock"]["name"] == lot1.feedstock.name][0]
        self.assertEqual(quota_line_1["year"], start_year)
        # self.assertEqual(quota_line_1["feedstock"]["name"], lot2.feedstock.name)
        self.assertEqual(quota_line_1["production_tonnes"], round(prod1_tonnes))
        self.assertEqual(quota_line_1["lot_count"], 2)  # 2 lots created in create_lots()
        self.assertEqual(quota_line_1["quotas_progression"], round(prod1_progression, 2))

        quota_line_2 = [q for q in quotas if q["feedstock"]["name"] == lot3.feedstock.name][0]
        self.assertEqual(quota_line_2["production_tonnes"], round(lot3.weight / 1000))
        # without
        agreement.application = None
        agreement.save()
        response = self.client.get(
            reverse("double-counting-agreements-detail", kwargs={"id": agreement_id}),
            {"entity_id": self.admin.id, "agreement_id": agreement_id},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["application"] is None
        assert data["quotas"] is None
        assert not data["has_dechets_industriels"]
