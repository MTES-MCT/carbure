# test with : python web/manage.py test transactions.sanity_checks.tests.tests_double_counting.DoubleCountingSanityChecksTest --keepdb

import datetime
from pprint import pprint
import certifi
from django.test import TestCase
from certificates.models import DoubleCountingRegistration

from core.carburetypes import CarbureCertificatesErrors, CarbureSanityCheckErrors
from core.models import CarbureLot, Entity, MatierePremiere
from doublecount.factories.agreement import DoubleCountingRegistrationFactory
from doublecount.factories.application import DoubleCountingApplicationFactory
from doublecount.factories.production import DoubleCountingProductionFactory
from doublecount.factories.sourcing import DoubleCountingSourcingFactory
from doublecount.models import DoubleCountingApplication
from producers.models import ProductionSite
from transactions.factories import CarbureLotFactory
from transactions.models import LockedYear
from ..helpers import enrich_lot, has_error, get_prefetched_data
from ..sanity_checks import sanity_checks


class DoubleCountingSanityChecksTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/ml.json",
    ]

    def setUp(self):
        self.dc_feedstock = MatierePremiere.objects.filter(is_double_compte=True).first()
        self.other_feedstock = MatierePremiere.objects.exclude(is_double_compte=True).first()

        self.production_site = ProductionSite.objects.first()
        self.producer = self.production_site.producer

        self.old_dc_cert = DoubleCountingRegistration.objects.create(
            certificate_id="FR_00999_2021",
            production_site=self.production_site,
            valid_from=datetime.date(2021, 1, 1),
            valid_until=datetime.date(2022, 12, 31),
        )

        self.dc_cert = DoubleCountingRegistration.objects.create(
            certificate_id="FR_00999_2023",
            production_site=self.production_site,
            valid_from=datetime.date(2023, 1, 1),
            valid_until=datetime.date(2024, 12, 31),
        )

        self.future_dc_cert = DoubleCountingRegistration.objects.create(
            certificate_id="FR_00999_2025",
            production_site=self.production_site,
            valid_from=datetime.date(2025, 1, 1),
            valid_until=datetime.date(2026, 12, 31),
        )

        self.other_production_site = ProductionSite.objects.exclude(producer=self.producer).last()

        self.other_dc_cert = DoubleCountingRegistration.objects.create(
            certificate_id="FR_09999_2023",
            production_site=self.other_production_site,
            valid_from=datetime.date(2023, 1, 1),
            valid_until=datetime.date(2024, 12, 31),
        )

        self.free_dc_cert = DoubleCountingRegistration.objects.create(
            certificate_id="FR_99999_2023",
            production_site=None,
            valid_from=datetime.date(2023, 1, 1),
            valid_until=datetime.date(2024, 12, 31),
        )

        self.prefetched_data = get_prefetched_data()

    def run_checks(self, lot, prefetched_data=None):
        return sanity_checks(lot, prefetched_data or self.prefetched_data)

    def create_lot(self, **kwargs):
        lot = CarbureLotFactory.create(**kwargs)
        return enrich_lot(lot)

    def test_missing_ref_dbl_counting(self):
        error = CarbureSanityCheckErrors.MISSING_REF_DBL_COUNTING

        lot = self.create_lot(
            feedstock=self.other_feedstock,
            production_site_double_counting_certificate="",
        )

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.feedstock = self.dc_feedstock

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.production_site_double_counting_certificate = "FR_00999_2023"

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_unknown_double_counting_certificate_unknown_production_site(self):
        error = CarbureCertificatesErrors.UNKNOWN_DOUBLE_COUNTING_CERTIFICATE

        lot = self.create_lot(
            feedstock=self.dc_feedstock,
            carbure_producer=None,
            carbure_production_site=None,
        )

        # case 1: unknown production site + unknown DC cert => error
        lot.production_site_double_counting_certificate = "FR_123456789_2050"
        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        # case 2: unknown production site + known DC cert => ok
        lot.production_site_double_counting_certificate = self.dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_unknown_double_counting_certificate_known_production_site(self):
        error = CarbureCertificatesErrors.UNKNOWN_DOUBLE_COUNTING_CERTIFICATE

        lot = self.create_lot(
            feedstock=self.dc_feedstock,
            carbure_producer=self.producer,
            carbure_production_site=self.production_site,
        )

        # case 1: known production site + unknown DC cert => error
        lot.production_site_double_counting_certificate = "FR_123456789_2050"
        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        # case 2: known production site + known DC cert of wrong psite => error
        lot.production_site_double_counting_certificate = self.other_dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        # case 3: known production site + known DC cert of right psite => ok
        lot.production_site_double_counting_certificate = self.dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        # case 4: known production site + known DC cert without linked prod site => ok
        lot.production_site_double_counting_certificate = self.free_dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_expired_double_counting_certificate(self):
        error = CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE

        lot = self.create_lot(
            feedstock=self.dc_feedstock,
            carbure_producer=self.producer,
            carbure_production_site=self.production_site,
            delivery_date=datetime.date(2023, 7, 1),
        )

        # case 1: dc reference is expired
        lot.production_site_double_counting_certificate = self.old_dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        # case 1: dc reference is up to date
        lot.production_site_double_counting_certificate = self.dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_invalid_double_counting_certificate(self):
        error = CarbureCertificatesErrors.INVALID_DOUBLE_COUNTING_CERTIFICATE

        lot = self.create_lot(
            feedstock=self.dc_feedstock,
            carbure_producer=self.producer,
            carbure_production_site=self.production_site,
            delivery_date=datetime.date(2023, 7, 1),
        )

        # case 1: dc reference is in the future
        lot.production_site_double_counting_certificate = self.future_dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        # case 1: dc reference is up to date
        lot.production_site_double_counting_certificate = self.dc_cert.certificate_id
        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_valid_double_counting_quotas(self):
        ### Prerequis
        requested_start_year = 2023
        approved_quota = 15000

        # on crée un dossier double comptage pour le producteur à partir de l'agrement
        app = DoubleCountingApplicationFactory.create(
            producer=self.production_site.producer,
            production_site=self.production_site,
            period_start__year=requested_start_year,
            status=DoubleCountingApplication.ACCEPTED,
            agreement_id=self.dc_cert.certificate_id,
        )
        self.dc_cert.application = app
        self.dc_cert.save()
        self.prefetched_data = get_prefetched_data()

        # on defini un quota pour un couple feedstock/biofuel pour le producteur
        sourcing = DoubleCountingSourcingFactory.create(dca=app, year=requested_start_year)

        production = DoubleCountingProductionFactory.create(
            dca=app,
            feedstock=sourcing.feedstock,
            year=requested_start_year,
            approved_quota=approved_quota,
        )

        ### Test
        error = CarbureSanityCheckErrors.EXCEEDED_DOUBLE_COUNTING_QUOTAS

        def create_dc_lot(weight):
            return self.create_lot(
                feedstock=production.feedstock,
                biofuel=production.biofuel,
                weight=weight,
                carbure_producer=self.producer,
                carbure_production_site=self.production_site,
                delivery_date=datetime.date(requested_start_year, 7, 1),
                production_site_double_counting_certificate=self.dc_cert.certificate_id,
                lot_status=CarbureLot.ACCEPTED,
            )

        # ajouter un lot avec ce couple feedstock/biofuel sur le producteur avec un volume inferieur au quota
        lot1 = create_dc_lot(weight=approved_quota - 1000)

        # on verifie que le lot passe sans warning
        error_list = self.run_checks(lot1)
        self.assertFalse(has_error(error, error_list))

        # ajouter un autre lot qui depasse le quota
        lot2 = create_dc_lot(weight=5000)

        # on verifie que le lot renvoie le warning CarbureSanityCheckErrors.EXCEEDED_DOUBLE_COUNTING_QUOTAS
        error_list = self.run_checks(lot2)
        self.assertTrue(has_error(error, error_list))
