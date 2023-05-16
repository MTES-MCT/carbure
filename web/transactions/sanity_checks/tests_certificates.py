import datetime
from django.test import TestCase

from core.carburetypes import CarbureCertificatesErrors, CarbureSanityCheckErrors
from core.models import Entity, MatierePremiere
from api.v4.sanity_checks import get_prefetched_data
from transactions.factories import CarbureLotFactory
from transactions.models import LockedYear
from .ghg import oct2015, jan2021
from .helpers import enrich_lot, has_error, july1st2021
from .sanity_checks import sanity_checks


class GhgSanityChecksTest(TestCase):
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
        errors = sanity_checks(lot, prefetched_data or self.prefetched_data)
        return errors

    def create_lot(self, **kwargs):
        lot = CarbureLotFactory.create(**kwargs)
        return enrich_lot(lot)

    def x_test_unknown_double_counting_certificate(self):
        error = CarbureCertificatesErrors.UNKNOWN_DOUBLE_COUNTING_CERTIFICATE

    def x_test_expired_double_counting_certificate(self):
        error = CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE

    def x_test_invalid_double_counting_certificate(self):
        error = CarbureCertificatesErrors.INVALID_DOUBLE_COUNTING_CERTIFICATE
