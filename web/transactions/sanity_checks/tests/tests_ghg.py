import datetime

from django.test import TestCase

from core.carburetypes import CarbureMLGHGErrors, CarbureSanityCheckErrors
from core.models import Entity, MatierePremiere
from ml.models import ETDStats
from transactions.factories import CarbureLotFactory

from ..ghg import jan2021, oct2015
from ..helpers import enrich_lot, get_prefetched_data, has_error, july1st2021
from ..sanity_checks import sanity_checks


class GhgSanityChecksTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
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

    def test_ghg_reduc_sup_100(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_SUP_100

        # prepare a lot for RED I values
        lot_red_i = self.create_lot(
            delivery_date=july1st2021 - datetime.timedelta(days=15),
            ghg_reduction=95,
            ghg_reduction_red_ii=105,  # put a wrong RED II value to confirm it will be ignored
        )

        error_list = self.run_checks(lot_red_i)
        assert not has_error(error, error_list)

        lot_red_i.ghg_reduction = 105

        error_list = self.run_checks(lot_red_i)
        assert has_error(error, error_list)

        # prepare a lot for RED II values
        lot_red_ii = self.create_lot(
            delivery_date=july1st2021 + datetime.timedelta(days=15),
            ghg_reduction_red_ii=95,
            ghg_reduction=105,  # put a wrong RED I value to confirm it will be ignored
        )

        error_list = self.run_checks(lot_red_ii)
        assert not has_error(error, error_list)

        lot_red_ii.ghg_reduction_red_ii = 105

        error_list = self.run_checks(lot_red_ii)
        assert has_error(error, error_list)

    def test_ghg_reduc_sup_99(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_SUP_99

        # prepare a lot for RED II values
        lot = self.create_lot(
            delivery_date=july1st2021 + datetime.timedelta(days=15),
            ghg_reduction_red_ii=95,
            ghg_reduction=105,  # put a wrong RED I value to confirm it will be ignored
        )

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.ghg_reduction_red_ii = 99.9

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_ghg_reduc_inf_50(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_INF_50

        # prepare a lot for RED II values
        lot = self.create_lot(
            delivery_date=july1st2021 + datetime.timedelta(days=15),
            ghg_reduction_red_ii=95,
            ghg_reduction=105,  # put a wrong RED I value to confirm it will be ignored
        )

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.ghg_reduction_red_ii = 5

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_ghg_etd_0(self):
        error = CarbureSanityCheckErrors.GHG_ETD_0

        lot = self.create_lot(etd=1)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.etd = -1

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_ghg_ep_0(self):
        error = CarbureSanityCheckErrors.GHG_EP_0

        lot = self.create_lot(ep=1)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.ep = -1

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_ghg_el_neg(self):
        error = CarbureSanityCheckErrors.GHG_EL_NEG

        lot = self.create_lot(el=1)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.el = -1

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_ghg_eec_0(self):
        error = CarbureSanityCheckErrors.GHG_EEC_0

        conv_feedstock = MatierePremiere.objects.filter(category="CONV").first()
        other_feedstock = MatierePremiere.objects.exclude(category="CONV").first()

        lot = self.create_lot(eec=0, feedstock=other_feedstock)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.eec = 1
        lot.feedstock = conv_feedstock

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.eec = 0

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_eec_with_residue(self):
        error = CarbureSanityCheckErrors.EEC_WITH_RESIDUE

        conv_feedstock = MatierePremiere.objects.filter(category="CONV").exclude(code="EP2").first()
        other_feedstock = MatierePremiere.objects.exclude(category="CONV", code="EP2").first()
        ep2 = MatierePremiere.objects.get(code="EP2")

        lot = self.create_lot(feedstock=other_feedstock, eec=1)

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

        lot.eec = 0

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.eec = 1
        lot.feedstock = conv_feedstock

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.eec = 1
        lot.feedstock = ep2

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

    def test_ghg_reduc_inf_60(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_INF_60

        lot = self.create_lot(production_site_commissioning_date=None)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.production_site_commissioning_date = oct2015 + datetime.timedelta(days=15)
        lot.ghg_reduction_red_ii = 61

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.ghg_reduction_red_ii = 59

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_ghg_reduc_inf_65(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_INF_65

        lot = self.create_lot(production_site_commissioning_date=None)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.production_site_commissioning_date = jan2021 + datetime.timedelta(days=15)
        lot.ghg_reduction_red_ii = 64

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

        lot.ghg_reduction_red_ii = 66

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

    def test_etd_anormal_high(self):
        error = CarbureMLGHGErrors.ETD_ANORMAL_HIGH

        etd = ETDStats.objects.first()
        if not etd:
            return

        lot = self.create_lot(feedstock=etd.feedstock, etd=1)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.etd = max(2 * etd.default_value, 5) + 1
        error_list = self.run_checks(lot)

        assert has_error(error, error_list)

    def test_etd_no_eu_too_low(self):
        pass

    def x_test_etd_eu_default_value(self):
        pass

    def x_test_eec_anormal_low(self):
        pass

    def x_test_eec_anormal_high(self):
        pass

    def x_test_ep_anormal_low(self):
        pass

    def x_test_ep_anormal_high(self):
        pass
