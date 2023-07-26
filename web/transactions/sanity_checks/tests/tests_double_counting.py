import datetime
from django.test import TestCase
from certificates.models import DoubleCountingRegistration

from core.carburetypes import CarbureCertificatesErrors, CarbureSanityCheckErrors
from core.models import Entity, MatierePremiere
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
