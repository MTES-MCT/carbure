from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice

from core.carburetypes import CarbureError
from core.models import CarbureLot, CarbureStock, Entity, Pays, UserRights
from transactions.api.lots.tests.tests_utils import get_lot
from transactions.factories.certificate import GenericCertificateFactory
from transactions.models import Depot, ProductionSite, YearConfig


class LotsFlowTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        user_model = get_user_model()
        # let's create a user
        self.password = "totopouet"
        self.user1 = user_model.objects.create_user(
            email="testuser1@toto.com",
            name="Le Super Testeur 1",
            password=self.password,
        )
        loggedin = self.client.login(username=self.user1.email, password=self.password)
        assert loggedin
        self.producer = (
            Entity.objects.filter(entity_type=Entity.PRODUCER)
            .annotate(psites=Count("entitysite__site"))
            .filter(psites__gt=0)[0]
        )
        self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        self.trader.default_certificate = "TRADER_CERTIFICATE"
        self.trader.save()
        self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        UserRights.objects.update_or_create(entity=self.producer, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.trader, user=self.user1, role=UserRights.RW)
        UserRights.objects.update_or_create(entity=self.operator, user=self.user1, role=UserRights.RW)

        GenericCertificateFactory.create(
            certificate_id="VALID",
            valid_from=date(2000, 1, 1),
            valid_until=date(3000, 1, 1),
        )

        # pass otp verification
        response = self.client.get(reverse("auth-request-otp"))
        assert response.status_code == 200
        device, created = EmailDevice.objects.get_or_create(user=self.user1)
        response = self.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
        assert response.status_code == 200

    def create_draft_v2(self, **kwargs):
        lot = get_lot(self.producer)
        lot.update(kwargs)
        return self.client.post(reverse("transactions-lots-add"), lot)

    def create_draft(self, lot=None, **kwargs):
        if lot is None:
            lot = get_lot(self.producer)
        lot["supplier_certificate"] = "VALID"
        lot.update(kwargs)
        response = self.client.post(reverse("transactions-lots-add"), lot)
        assert response.status_code == 200
        data = response.json()["data"]
        lot_id = data["id"]
        lot = CarbureLot.objects.get(id=lot_id)
        return lot

    def send_lot(self, lot):
        response = self.client.post(
            reverse("transactions-lots-send"),
            {"entity_id": self.producer.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        return lot

    def test_create_draft(self, **kwargs):
        YearConfig.objects.create(year=2018, locked=True)  # 2021 is the right year
        lot = self.create_draft(**kwargs)
        assert lot.lot_status == CarbureLot.DRAFT

    def test_create_draft_on_locked_year(self, **kwargs):
        YearConfig.objects.create(year=2021, locked=True)
        lot = get_lot(self.producer)
        lot.update(kwargs)
        response = self.client.post(reverse("transactions-lots-add"), lot)
        assert response.status_code == 200
        lot_id = response.json()["data"]["id"]

        response = self.client.get(
            reverse("transactions-lots-details"),
            {"lot_id": lot_id, "entity_id": self.producer.id},
        )
        errors = response.json()["data"]["errors"]
        assert errors[0]["error"] == CarbureError.YEAR_LOCKED

    def test_update_lot(self):
        YearConfig.objects.create(year=2018, locked=True)
        lotdata = get_lot(entity=self.producer)
        lot = self.create_draft(lot=lotdata)
        lotdata["lot_id"] = lot.id
        lotdata["volume"] = 42000
        lotdata["delivery_date"] = "01/01/2022"
        response = self.client.post(reverse("transactions-lots-update"), lotdata)
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.volume == 42000
        assert lot.year == 2022

    def test_delete_lot(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("transactions-lots-delete"),
            {"entity_id": self.producer.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        assert not CarbureLot.objects.filter(id=lot.id).exists()

        lot = self.send_lot(self.create_draft())
        response = self.client.post(
            reverse("transactions-lots-delete"),
            {"entity_id": self.producer.id, "selection": [lot.id]},
        )  # cannot delete a lot not in draft
        assert response.status_code == 200
        lot.refresh_from_db()
        assert lot.lot_status == CarbureLot.DELETED

        lot = self.create_draft()
        response = self.client.post(
            reverse("transactions-lots-delete"),
            {"entity_id": self.trader.id, "selection": [lot.id]},
        )  # cannot delete someone else's lot
        assert response.status_code == 400

    def test_duplicate_lot(self):
        lot = self.create_draft()
        response = self.client.post(
            reverse("transactions-lots-duplicate"),
            {"entity_id": self.producer.id, "lot_id": lot.id},
        )
        assert response.status_code == 200
        response = self.client.post(
            reverse("transactions-lots-duplicate"),
            {"entity_id": self.trader.id, "lot_id": lot.id},
        )
        assert response.status_code == 403

    def test_send(self):
        lot = self.create_draft()
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING

    def test_send_trading_preserves_delivery_type_on_child(self):
        for delivery_type in (CarbureLot.UNKNOWN, CarbureLot.DIRECT):
            with self.subTest(delivery_type=delivery_type):
                lot = self.create_draft(
                    production_site_commissioning_date="12/12/2012",
                    vendor_certificate="VALID",
                    carbure_producer="",
                    carbure_production_site="",
                    unknown_producer="BIOFUEL GMBH",
                    carbure_client_id=self.operator.id,
                    delivery_type=delivery_type,
                    delivery_site_country_code="FR",
                    unknown_dispatch_site="Dispatch site",
                    dispatch_site_country_code="FR",
                    usage=CarbureLot.USAGE_ROAD,
                )
                self.assertEqual(lot.carbure_vendor, self.producer)
                self.assertEqual(lot.delivery_type, delivery_type)

                lot = self.send_lot(lot)
                child = CarbureLot.objects.get(parent_lot=lot)

                self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
                self.assertEqual(lot.delivery_type, CarbureLot.TRADING)
                self.assertEqual(lot.carbure_client, self.producer)
                self.assertEqual(child.lot_status, CarbureLot.PENDING)
                self.assertEqual(child.delivery_type, delivery_type)
                self.assertEqual(child.carbure_supplier, self.producer)
                self.assertEqual(child.carbure_client, self.operator)

    def test_send_trading_parent_delivery_site(self):
        dispatch_depot = Depot.objects.create(
            name="Dispatch depot", customs_id="DETEST", country=Pays.objects.get(code_pays="DE")
        )
        production_site = ProductionSite.objects.filter(created_by=self.producer).first()
        delivery_depot = Depot.objects.filter(country__code_pays="FR").first()

        for dispatch_site, delivery_site in (
            (dispatch_depot, None),
            (production_site, None),
            (dispatch_depot, delivery_depot),
            (None, None),
        ):
            with self.subTest(dispatch_site=dispatch_site, delivery_site=delivery_site):
                lot = self.create_draft(
                    production_site_commissioning_date="12/12/2012",
                    vendor_certificate="VALID",
                    carbure_producer="",
                    carbure_production_site="",
                    unknown_producer="BIOFUEL GMBH",
                    carbure_client_id=self.operator.id,
                    delivery_type=CarbureLot.DIRECT,
                    carbure_delivery_site_depot_id=delivery_site.depot_id if delivery_site else "UNKNOWN_DEPOT",
                    unknown_delivery_site="Final delivery site",
                    carbure_dispatch_site_id=dispatch_site.pk if dispatch_site else "",
                    unknown_dispatch_site="Dispatch site",
                    dispatch_site_country_code="DE",
                    usage=CarbureLot.USAGE_ROAD,
                )
                original_delivery_country = lot.delivery_site_country
                original_unknown_delivery_site = lot.unknown_delivery_site
                expected_delivery_site = delivery_site or getattr(dispatch_site, "depot", None)
                expected_delivery_country = (
                    lot.dispatch_site_country if delivery_site is None and dispatch_site else original_delivery_country
                )

                lot = self.send_lot(lot)
                child = CarbureLot.objects.get(parent_lot=lot)

                self.assertEqual(lot.carbure_delivery_site, expected_delivery_site)
                self.assertEqual(lot.delivery_site_country, expected_delivery_country)
                self.assertIsNone(lot.unknown_delivery_site)
                self.assertEqual(child.carbure_delivery_site, delivery_site)
                self.assertEqual(child.delivery_site_country, original_delivery_country)
                self.assertEqual(child.unknown_delivery_site, original_unknown_delivery_site)

    def test_send_trading_auto_accepts_child_with_unknown_client(self):
        efpe = Depot.objects.filter(site_type=Depot.EFPE).first()
        for delivery_type in (CarbureLot.RFC, CarbureLot.DIRECT, CarbureLot.EXPORT):
            with self.subTest(delivery_type=delivery_type):
                lot = self.create_draft(
                    production_site_commissioning_date="12/12/2012",
                    vendor_certificate="VALID",
                    carbure_producer="",
                    carbure_production_site="",
                    unknown_producer="BIOFUEL GMBH",
                    carbure_client_id="",
                    unknown_client="External client",
                    delivery_type=delivery_type,
                    carbure_delivery_site_depot_id=efpe.depot_id,
                    unknown_dispatch_site="Dispatch site",
                    dispatch_site_country_code="FR",
                    usage=CarbureLot.USAGE_ROAD,
                )
                self.assertEqual(lot.carbure_vendor, self.producer)
                response = self.client.post(
                    reverse("transactions-lots-send"),
                    {"entity_id": self.producer.id, "selection": [lot.id]},
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["data"]["auto-accepted"], 2)
                lot.refresh_from_db()
                child = CarbureLot.objects.get(parent_lot=lot)

                self.assertEqual(lot.lot_status, CarbureLot.ACCEPTED)
                self.assertEqual(lot.delivery_type, CarbureLot.TRADING)
                self.assertEqual(child.lot_status, CarbureLot.ACCEPTED)
                self.assertEqual(child.delivery_type, delivery_type)
                self.assertIsNone(child.carbure_client)
                self.assertEqual(child.unknown_client, "External client")

    def test_accept_in_stock(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)

        response = self.client.post(
            reverse("transactions-lots-accept-in-stock"),
            {"entity_id": self.trader.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.STOCK
        stock = CarbureStock.objects.filter(parent_lot=lot).count()
        assert stock == 1

    def test_accept_rfc(self):
        """Accept a lot as RFC (Release for Consumption)."""
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN
        response = self.client.post(
            reverse("transactions-lots-accept-release-for-consumption"),
            {
                "entity_id": self.operator.id,
                "selection": [lot.id],
                "usage": CarbureLot.USAGE_ROAD,
            },
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.RFC
        assert lot.usage == CarbureLot.USAGE_ROAD
        assert lot.usage_precision == ""

    def test_accept_rfc_requires_usage(self):
        """Usage is required to accept a lot as RFC."""
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)

        response = self.client.post(
            reverse("transactions-lots-accept-release-for-consumption"),
            {"entity_id": self.operator.id, "selection": [lot.id]},
        )

        assert response.status_code == 400
        lot.refresh_from_db()
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

    def test_accept_rfc_requires_usage_precision_for_other(self):
        """Usage precision is required when usage is 'other'."""
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)

        response = self.client.post(
            reverse("transactions-lots-accept-release-for-consumption"),
            {
                "entity_id": self.operator.id,
                "selection": [lot.id],
                "usage": CarbureLot.USAGE_OTHER,
            },
        )

        assert response.status_code == 400
        lot.refresh_from_db()
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

    def test_accept_rfc_stores_usage_precision_for_other(self):
        """Usage precision is stored when usage is 'other'."""
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)

        response = self.client.post(
            reverse("transactions-lots-accept-release-for-consumption"),
            {
                "entity_id": self.operator.id,
                "selection": [lot.id],
                "usage": CarbureLot.USAGE_OTHER,
                "usage_precision": "Usage expérimental",
            },
        )

        assert response.status_code == 200
        lot.refresh_from_db()
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.RFC
        assert lot.usage == CarbureLot.USAGE_OTHER
        assert lot.usage_precision == "Usage expérimental"

    def test_send_rfc(self):
        efpe = Depot.objects.filter(site_type=Depot.EFPE).first()
        assert efpe is not None

        lot = self.create_draft(
            unknown_client="CLIENT MAC",
            delivery_type="RFC",
            carbure_client_id="",
            carbure_delivery_site_depot_id=efpe.depot_id,
            usage=CarbureLot.USAGE_ROAD,
        )
        assert lot.usage == CarbureLot.USAGE_ROAD
        assert lot.usage_precision == ""
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.RFC

    def test_accept_trading_to_carbure_client(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

        response = self.client.post(
            reverse("transactions-lots-accept-trading"),
            {
                "entity_id": self.trader.id,
                "selection": [lot.id],
                "client_entity_id": self.operator.id,
            },
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.TRADING
        child = CarbureLot.objects.get(parent_lot=lot)
        assert child.lot_status == CarbureLot.PENDING
        assert child.delivery_type == CarbureLot.UNKNOWN

    def test_accept_trading_to_unknown_client(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

        response = self.client.post(
            reverse("transactions-lots-accept-trading"),
            {
                "entity_id": self.trader.id,
                "selection": [lot.id],
                "unknown_client": "TRADER CLIENT",
            },
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.TRADING
        child = CarbureLot.objects.get(parent_lot=lot)
        assert child.lot_status == CarbureLot.ACCEPTED
        assert child.delivery_type == CarbureLot.UNKNOWN

    def test_accept_processing(self):
        lot = self.create_draft(carbure_client_id=self.trader.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN

        response = self.client.post(
            reverse("transactions-lots-accept-processing"),
            {
                "entity_id": self.trader.id,
                "selection": [lot.id],
                "processing_entity_id": self.operator.id,
            },
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.PROCESSING
        child = CarbureLot.objects.get(parent_lot=lot)
        assert child.lot_status == CarbureLot.PENDING
        assert child.delivery_type == CarbureLot.UNKNOWN

    def test_accept_blending(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN
        response = self.client.post(
            reverse("transactions-lots-accept-blending"),
            {"entity_id": self.operator.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.BLENDING

    def test_accept_export(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        assert lot.lot_status == CarbureLot.PENDING
        assert lot.delivery_type == CarbureLot.UNKNOWN
        response = self.client.post(
            reverse("transactions-lots-accept-export"),
            {"entity_id": self.operator.id, "selection": [lot.id]},
        )
        assert response.status_code == 200
        lot = CarbureLot.objects.get(id=lot.id)
        assert lot.lot_status == CarbureLot.ACCEPTED
        assert lot.delivery_type == CarbureLot.EXPORT

    def test_accept_direct_delivery(self):
        for usage, expected_precision in ((CarbureLot.USAGE_ROAD, ""), (CarbureLot.USAGE_OTHER, "Details")):
            with self.subTest(usage=usage):
                lot = self.create_draft(carbure_client_id=self.operator.id)
                lot = self.send_lot(lot)
                response = self.client.post(
                    reverse("transactions-lots-accept-direct-delivery"),
                    {
                        "entity_id": self.operator.id,
                        "selection": [lot.id],
                        "usage": usage,
                        "usage_precision": "Details",
                    },
                )
                assert response.status_code == 200
                lot.refresh_from_db()
                assert lot.lot_status == CarbureLot.ACCEPTED
                assert lot.delivery_type == CarbureLot.DIRECT
                assert lot.usage == usage
                assert lot.usage_precision == expected_precision

    def test_accept_direct_delivery_requires_usage_fields(self):
        lot = self.create_draft(carbure_client_id=self.operator.id)
        lot = self.send_lot(lot)
        for fields in ({}, {"usage": "INVALID"}, {"usage": CarbureLot.USAGE_OTHER, "usage_precision": " "}):
            with self.subTest(fields=fields):
                response = self.client.post(
                    reverse("transactions-lots-accept-direct-delivery"),
                    {"entity_id": self.operator.id, "selection": [lot.id], **fields},
                )
                assert response.status_code == 400
                lot.refresh_from_db()
                assert lot.lot_status == CarbureLot.PENDING
                assert lot.delivery_type == CarbureLot.UNKNOWN
