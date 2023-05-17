import datetime
from django.test import TestCase

from core.carburetypes import CarbureCertificatesErrors, CarbureSanityCheckErrors
from core.models import Entity, MatierePremiere
from api.v4.sanity_checks import get_prefetched_data
from resources.factories.production_site import ProductionSiteFactory
from transactions.factories import CarbureLotFactory
from transactions.models import LockedYear
from ..helpers import enrich_lot, has_error
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
        self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).first()
        LockedYear.objects.create(year=2016, locked=True)

        self.prefetched_data = get_prefetched_data()

    def run_checks(self, lot, prefetched_data=None):
        return sanity_checks(lot, prefetched_data or self.prefetched_data)

    def create_lot(self, **kwargs):
        lot = CarbureLotFactory.create(**kwargs)
        return enrich_lot(lot)

    def test_missing_ref_dbl_counting(self):
        error = CarbureSanityCheckErrors.MISSING_REF_DBL_COUNTING

        dc_feedstock = MatierePremiere.objects.filter(is_double_compte=True).first()
        other_feedstock = MatierePremiere.objects.exclude(is_double_compte=True).first()

        lot = self.create_lot(
            feedstock=other_feedstock,
            production_site_double_counting_certificate="",
        )

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.feedstock = dc_feedstock

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.production_site_double_counting_certificate = "FR_123_2023"

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def x_test_unknown_double_counting_certificate(self):
        error = CarbureCertificatesErrors.UNKNOWN_DOUBLE_COUNTING_CERTIFICATE

    def x_test_expired_double_counting_certificate(self):
        error = CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE

    def x_test_invalid_double_counting_certificate(self):
        error = CarbureCertificatesErrors.INVALID_DOUBLE_COUNTING_CERTIFICATE
