import datetime
from django.test import TestCase

from core.carburetypes import CarbureSanityCheckErrors, CarbureCertificatesErrors
from core.models import Entity, CarbureLot, MatierePremiere, Biocarburant, Depot, Pays
from transactions.factories import CarbureLotFactory
from transactions.models import LockedYear
from producers.models import ProductionSite
from ..helpers import enrich_lot, has_error, get_prefetched_data
from ..sanity_checks import sanity_checks


class MandatorySanityChecksTest(TestCase):
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
        self.prefetched_data = get_prefetched_data()

    def run_checks(self, lot, prefetched_data=None):
        return sanity_checks(lot, prefetched_data or self.prefetched_data)

    def create_lot(self, **kwargs):
        lot = CarbureLotFactory.create(**kwargs)
        return enrich_lot(lot)

    def test_missing_volume(self):
        error = CarbureSanityCheckErrors.MISSING_VOLUME

        lot = self.create_lot(volume=10000)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.volume = 0

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_missing_biofuel(self):
        error = CarbureSanityCheckErrors.MISSING_BIOFUEL

        lot = self.create_lot(biofuel=Biocarburant.objects.first())

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.biofuel = None

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_missing_feedstock(self):
        error = CarbureSanityCheckErrors.MISSING_FEEDSTOCK

        lot = self.create_lot(feedstock=MatierePremiere.objects.first())

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.feedstock = None

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_unknown_production_site(self):
        error = CarbureSanityCheckErrors.UNKNOWN_PRODUCTION_SITE

        lot = self.create_lot(carbure_producer=self.producer, carbure_production_site=ProductionSite.objects.first())

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.carbure_production_site = None

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_missing_production_site_comdate(self):
        error = CarbureSanityCheckErrors.MISSING_PRODUCTION_SITE_COMDATE

        lot = self.create_lot(carbure_producer=self.producer, carbure_production_site=ProductionSite.objects.first())

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.carbure_production_site = None
        lot.production_site_commissioning_date = None

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_missing_transport_document_reference(self):
        error = CarbureSanityCheckErrors.MISSING_TRANSPORT_DOCUMENT_REFERENCE

        lot = self.create_lot(delivery_type=CarbureLot.RFC, transport_document_reference="")

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.delivery_type = CarbureLot.BLENDING

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.transport_document_reference = "ABCD"

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_missing_carbure_delivery_site(self):
        error = CarbureSanityCheckErrors.MISSING_CARBURE_DELIVERY_SITE

        lot = self.create_lot(
            delivery_type=CarbureLot.RFC,
            carbure_delivery_site=None,
            delivery_site_country=Pays.objects.get(code_pays="FR"),
        )

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.delivery_type = CarbureLot.BLENDING

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.carbure_delivery_site = Depot.objects.first()

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_missing_carbure_client(self):
        error = CarbureSanityCheckErrors.MISSING_CARBURE_CLIENT

        lot = self.create_lot(
            delivery_type=CarbureLot.RFC,
            carbure_client=None,
            delivery_site_country=Pays.objects.get(code_pays="FR"),
        )

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.delivery_type = CarbureLot.BLENDING

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.carbure_client = self.producer

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_missing_delivery_date(self):
        error = CarbureSanityCheckErrors.MISSING_DELIVERY_DATE

        # @TODO testing delivery_date=None actually breaks other sanity checks, fix that

        # lot = self.create_lot(delivery_date=None)

        # error_list = self.run_checks(lot)
        # self.assertTrue(has_error(error, error_list))

        # lot.delivery_date = datetime.date.today()

        # error_list = self.run_checks(lot)
        # self.assertFalse(has_error(error, error_list))

    def test_wrong_delivery_date(self):
        error = CarbureSanityCheckErrors.WRONG_DELIVERY_DATE

        lot = self.create_lot(delivery_date=datetime.date.today())

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.delivery_date = datetime.date(2000, 1, 1)

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.delivery_date = datetime.date(2040, 1, 1)

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_missing_delivery_site_country(self):
        error = CarbureSanityCheckErrors.MISSING_DELIVERY_SITE_COUNTRY

        lot = self.create_lot(delivery_site_country=None)

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.delivery_site_country = Pays.objects.first()

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_missing_feedstock_country_of_origin(self):
        error = CarbureSanityCheckErrors.MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN

        country = Pays.objects.filter(is_in_europe=True).first()

        lot = self.create_lot(country_of_origin=None, delivery_site_country=country)

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.country_of_origin = country

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def x_test_missing_supplier_certificate(self):
        error = CarbureCertificatesErrors.MISSING_SUPPLIER_CERTIFICATE
