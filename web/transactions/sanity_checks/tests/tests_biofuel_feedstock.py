from django.test import TestCase

from core.carburetypes import CarbureSanityCheckErrors
from core.models import Biocarburant, Entity, MatierePremiere
from transactions.factories import CarbureLotFactory

from ..biofuel_feedstock import get_biofuel_feedstock_incompatibilities
from ..helpers import enrich_lot, get_prefetched_data, has_error
from ..sanity_checks import sanity_checks


class BiofuelFeedstockSanityChecksTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/ml.json",
        "json/entities_sites.json",
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

        colza = MatierePremiere.biofuel.get(code="COLZA")
        residus_viniques = MatierePremiere.biofuel.get(code="RESIDUS_VINIQUES")

        lot = self.create_lot(feedstock=colza)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.feedstock = residus_viniques

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def x_test_provenance_mp(self):
        pass

    def test_alcohol_biofuel_requires_alcohol_compatible_feedstock(self):
        alcohol = Biocarburant(code="ETH", is_alcool=True)
        feedstock = MatierePremiere.biofuel.get(code="COLZA")

        errors = list(get_biofuel_feedstock_incompatibilities(alcohol, feedstock))

        assert len(errors) == 1

    def test_hogpl_accepts_animal_fat_feedstock(self):
        hogpl = Biocarburant(code="HOGPL", is_graisse=True)
        feedstock = MatierePremiere.biofuel.get(code="HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2")

        errors = list(get_biofuel_feedstock_incompatibilities(hogpl, feedstock))

        assert not errors

    def test_hvogpl_requires_vegetable_oil_feedstock(self):
        hvogpl = Biocarburant(code="HVOGPL", is_graisse=True)
        vegetable_feedstock = MatierePremiere.biofuel.get(code="COLZA")
        non_vegetable_feedstock = MatierePremiere.biofuel.get(code="HUILE_ALIMENTAIRE_USAGEE")

        assert not list(get_biofuel_feedstock_incompatibilities(hvogpl, vegetable_feedstock))
        assert list(get_biofuel_feedstock_incompatibilities(hvogpl, non_vegetable_feedstock))

    def test_hcgpl_requires_supported_feedstock(self):
        hcgpl = Biocarburant(code="HCGPL", is_graisse=True)
        supported_feedstock = MatierePremiere.biofuel.get(code="COLZA")
        unsupported_feedstock = MatierePremiere.biofuel.get(code="BETTERAVE")

        assert not list(get_biofuel_feedstock_incompatibilities(hcgpl, supported_feedstock))
        assert list(get_biofuel_feedstock_incompatibilities(hcgpl, unsupported_feedstock))
