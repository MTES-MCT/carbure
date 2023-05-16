import datetime
from django.test import TestCase

from core.carburetypes import CarbureSanityCheckErrors, CarbureCertificatesErrors, CarbureMLGHGErrors
from core.models import Entity, CarbureLot, MatierePremiere, Biocarburant, Depot, EntityDepot, Pays
from ml.models import ETDStats, EECStats, EPStats
from api.v4.sanity_checks import sanity_check, get_prefetched_data, july1st2021, oct2015, jan2021
from transactions.factories import CarbureLotFactory
from transactions.models import LockedYear
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from resources.factories import ProductionSiteFactory
from .helpers import enrich_lot, has_error


class SanityChecksTest(TestCase):
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
        _, errors = sanity_check(lot, prefetched_data or self.prefetched_data)
        return errors

    def create_lot(self, **kwargs):
        lot = CarbureLotFactory.create(**kwargs)
        return enrich_lot(lot)

    def test_mac_bc_wrong(self):
        error = CarbureSanityCheckErrors.MAC_BC_WRONG

        eth = Biocarburant.objects.get(code="ETH")
        emag = Biocarburant.objects.get(code="EMAG")

        lot = self.create_lot(delivery_type=CarbureLot.BLENDING, biofuel=emag)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.delivery_type = CarbureLot.RFC

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.biofuel = eth

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_mac_not_efpe(self):
        error = CarbureSanityCheckErrors.MAC_NOT_EFPE

        efs = Depot.objects.filter(depot_type=Depot.EFS).first()
        efpe = Depot.objects.filter(depot_type=Depot.EFPE).first()

        lot = self.create_lot(delivery_type=CarbureLot.BLENDING, carbure_delivery_site=efs)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.delivery_type = CarbureLot.RFC

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.carbure_delivery_site = efpe

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_volume_faible(self):
        error = CarbureSanityCheckErrors.VOLUME_FAIBLE

        lot = self.create_lot(volume=2001)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.volume = 1999

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_year_locked(self):
        error = CarbureSanityCheckErrors.YEAR_LOCKED

        lot = self.create_lot(year=2023)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.year = 2016

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.year = 2015

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_deprecated_mp(self):
        error = CarbureSanityCheckErrors.DEPRECATED_MP

        colza = MatierePremiere.objects.get(code="COLZA")
        residus_viniques = MatierePremiere.objects.get(code="RESIDUS_VINIQUES")

        lot = self.create_lot(feedstock=colza)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.feedstock = residus_viniques

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def x_test_provenance_mp(self):
        error = CarbureSanityCheckErrors.PROVENANCE_MP
        pass

    def x_test_mp_bc_incoherent(self):
        error = CarbureSanityCheckErrors.MP_BC_INCOHERENT
        pass

    def test_missing_ref_dbl_counting(self):
        error = CarbureSanityCheckErrors.MISSING_REF_DBL_COUNTING

        dc_feedstock = MatierePremiere.objects.filter(is_double_compte=True).first()
        other_feedstock = MatierePremiere.objects.exclude(is_double_compte=True).first()

        lot = self.create_lot(
            feedstock=other_feedstock,
            carbure_production_site=None,
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

        lot.production_site_double_counting_certificate = ""
        lot.unknown_production_site = None
        lot.carbure_production_site = ProductionSiteFactory.create(eligible_dc=True, dc_reference="FR_123_2023")

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_mp_not_configured(self):
        error = CarbureSanityCheckErrors.MP_NOT_CONFIGURED

        feedstock = MatierePremiere.objects.first()
        other_feedstock = MatierePremiere.objects.last()
        production_site = ProductionSiteFactory.create(producer=self.producer)

        ProductionSiteInput.objects.create(production_site=production_site, matiere_premiere=feedstock)

        lot = self.create_lot(
            added_by=self.producer,
            feedstock=other_feedstock,
            carbure_production_site=production_site,
        )

        prefetched_data = get_prefetched_data(self.producer)

        error_list = self.run_checks(lot, prefetched_data)
        self.assertTrue(has_error(error, error_list))

        lot.feedstock = feedstock

        error_list = self.run_checks(lot, prefetched_data)
        self.assertFalse(has_error(error, error_list))

    def test_bc_not_configured(self):
        error = CarbureSanityCheckErrors.BC_NOT_CONFIGURED

        biofuel = Biocarburant.objects.first()
        other_biofuel = Biocarburant.objects.last()
        production_site = ProductionSiteFactory.create(producer=self.producer)

        ProductionSiteOutput.objects.create(production_site=production_site, biocarburant=biofuel)

        lot = self.create_lot(
            added_by=self.producer,
            biofuel=other_biofuel,
            carbure_production_site=production_site,
        )

        prefetched_data = get_prefetched_data(self.producer)

        error_list = self.run_checks(lot, prefetched_data)
        self.assertTrue(has_error(error, error_list))

        lot.biofuel = biofuel

        error_list = self.run_checks(lot, prefetched_data)
        self.assertFalse(has_error(error, error_list))

    def test_depot_not_configured(self):
        error = CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED

        depot = Depot.objects.first()
        other_depot = Depot.objects.last()

        lot = self.create_lot(
            added_by=self.producer,
            carbure_client=self.producer,
            carbure_delivery_site=other_depot,
            delivery_type=CarbureLot.BLENDING,
        )

        EntityDepot.objects.create(entity=self.producer, depot=depot)

        prefetched_data = get_prefetched_data(self.producer)

        error_list = self.run_checks(lot, prefetched_data)
        self.assertTrue(has_error(error, error_list))

        lot.carbure_delivery_site = depot

        error_list = self.run_checks(lot, prefetched_data)
        self.assertFalse(has_error(error, error_list))
