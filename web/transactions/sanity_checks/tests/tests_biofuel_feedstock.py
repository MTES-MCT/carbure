from django.test import TestCase

from core.carburetypes import CarbureSanityCheckErrors
from core.models import Entity, MatierePremiere
from transactions.factories import CarbureLotFactory

from ..helpers import enrich_lot, get_prefetched_data, has_error
from ..sanity_checks import sanity_checks


class BiofuelFeedstockSanityChecksTest(TestCase):
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

    def test_deprecated_mp(self):
        error = CarbureSanityCheckErrors.DEPRECATED_MP

        colza = MatierePremiere.objects.get(code="COLZA")
        residus_viniques = MatierePremiere.objects.get(code="RESIDUS_VINIQUES")

        lot = self.create_lot(feedstock=colza)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.feedstock = residus_viniques

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def x_test_provenance_mp(self):
        pass

    def x_test_mp_bc_incoherent(self):
        pass
