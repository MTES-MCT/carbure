import datetime

from django.test import TestCase

from core.carburetypes import CarbureSanityCheckErrors
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, SustainabilityDeclaration
from producers.models import ProductionSiteInput, ProductionSiteOutput
from resources.factories import ProductionSiteFactory
from transactions.factories import CarbureLotFactory
from transactions.models import Depot, EntitySite, YearConfig

from ..helpers import enrich_lot, get_prefetched_data, has_error
from ..sanity_checks import sanity_checks


class GeneralSanityChecksTest(TestCase):
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

    def test_mac_bc_wrong(self):
        error = CarbureSanityCheckErrors.MAC_BC_WRONG

        eth = Biocarburant.objects.get(code="ETH")
        emag = Biocarburant.objects.get(code="EMAG")

        lot = self.create_lot(delivery_type=CarbureLot.BLENDING, biofuel=emag)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.delivery_type = CarbureLot.RFC

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

        lot.biofuel = eth

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

    def test_mac_not_efpe(self):
        error = CarbureSanityCheckErrors.MAC_NOT_EFPE

        efs = Depot.objects.filter(site_type=Depot.EFS).first()
        efpe = Depot.objects.filter(site_type=Depot.EFPE).first()

        lot = self.create_lot(delivery_type=CarbureLot.BLENDING, carbure_delivery_site=efs)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.delivery_type = CarbureLot.RFC

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

        lot.carbure_delivery_site = efpe

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

    def test_volume_faible(self):
        error = CarbureSanityCheckErrors.VOLUME_FAIBLE

        lot = self.create_lot(volume=2001)

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        lot.volume = 1999

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

    def test_year_locked(self):
        error = CarbureSanityCheckErrors.YEAR_LOCKED

        lot = self.create_lot(
            lot_status=CarbureLot.PENDING,
            correction_status=CarbureLot.NO_PROBLEMO,
            year=2023,
        )

        error_list = self.run_checks(lot)
        assert not has_error(error, error_list)

        YearConfig.objects.create(year=2017, locked=True)
        prefetched_data = get_prefetched_data()

        lot.year = 2017

        error_list = self.run_checks(lot, prefetched_data)
        assert not has_error(error, error_list)

        lot.correction_status = CarbureLot.IN_CORRECTION

        error_list = self.run_checks(lot, prefetched_data)
        assert has_error(error, error_list)

        lot.year = 2010

        error_list = self.run_checks(lot)
        assert has_error(error, error_list)

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

        EntitySite.objects.create(entity=self.producer, site=depot)

        prefetched_data = get_prefetched_data(self.producer)

        error_list = self.run_checks(lot, prefetched_data)
        assert has_error(error, error_list)

        lot.carbure_delivery_site = depot

        error_list = self.run_checks(lot, prefetched_data)
        assert not has_error(error, error_list)

    def x_test_mp_not_configured(self):
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
        assert has_error(error, error_list)

        lot.feedstock = feedstock

        error_list = self.run_checks(lot, prefetched_data)
        assert not has_error(error, error_list)

    def x_test_bc_not_configured(self):
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
        assert has_error(error, error_list)

        lot.biofuel = biofuel

        error_list = self.run_checks(lot, prefetched_data)
        assert not has_error(error, error_list)

    def test_declaration_already_validated(self):
        error = CarbureSanityCheckErrors.DECLARATION_ALREADY_VALIDATED

        declaration = SustainabilityDeclaration.objects.create(
            entity=self.producer,
            period=datetime.date(2023, 1, 1),
            declared=True,
        )

        lot1 = self.create_lot(
            volume=2000,
            lot_status=CarbureLot.DRAFT,
            added_by=self.producer,
            period=202301,
        )

        lot2 = self.create_lot(
            volume=2000,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.IN_CORRECTION,
            added_by=self.producer,
            period=202301,
        )

        lot3 = self.create_lot(
            volume=2000,
            lot_status=CarbureLot.ACCEPTED,
            correction_status=CarbureLot.NO_PROBLEMO,
            added_by=self.producer,
            period=202301,
        )

        prefetched_data = get_prefetched_data(self.producer)

        error_list = self.run_checks(lot1, prefetched_data)
        assert has_error(error, error_list)

        error_list = self.run_checks(lot2, prefetched_data)
        assert has_error(error, error_list)

        error_list = self.run_checks(lot3, prefetched_data)
        assert not has_error(error, error_list)

        declaration.declared = False
        declaration.save()
        prefetched_data = get_prefetched_data(self.producer)

        error_list = self.run_checks(lot1, prefetched_data)
        assert not has_error(error, error_list)

        error_list = self.run_checks(lot2, prefetched_data)
        assert not has_error(error, error_list)

        declaration.declared = True
        declaration.save()
        prefetched_data = get_prefetched_data(self.producer)

        error_list = self.run_checks(lot1, prefetched_data)
        assert has_error(error, error_list)

        error_list = self.run_checks(lot2, prefetched_data)
        assert has_error(error, error_list)
