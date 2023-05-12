import datetime
from django.test import TestCase

from api.v4.tests_utils import setup_current_user
from core.carburetypes import CarbureSanityCheckErrors, CarbureCertificatesErrors, CarbureMLGHGErrors
from core.models import Entity, CarbureLot, MatierePremiere, Biocarburant, Depot, EntityDepot, Pays
from ml.models import ETDStats, EECStats, EPStats
from api.v4.sanity_checks import sanity_check, get_prefetched_data, july1st2021, oct2015, jan2021
from transactions.factories import CarbureLotFactory
from transactions.models import LockedYear
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from resources.factories import ProductionSiteFactory


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

    def test_ghg_reduc_sup_100(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_SUP_100

        # prepare a lot for RED I values
        lot_red_i = self.create_lot(
            delivery_date=july1st2021 - datetime.timedelta(days=15),
            ghg_reduction=95,
            ghg_reduction_red_ii=105,  # put a wrong RED II value to confirm it will be ignored
        )

        error_list = self.run_checks(lot_red_i)
        self.assertFalse(has_error(error, error_list))

        lot_red_i.ghg_reduction = 105

        error_list = self.run_checks(lot_red_i)
        self.assertTrue(has_error(error, error_list))

        # prepare a lot for RED II values
        lot_red_ii = self.create_lot(
            delivery_date=july1st2021 + datetime.timedelta(days=15),
            ghg_reduction_red_ii=95,
            ghg_reduction=105,  # put a wrong RED I value to confirm it will be ignored
        )

        error_list = self.run_checks(lot_red_ii)
        self.assertFalse(has_error(error, error_list))

        lot_red_ii.ghg_reduction_red_ii = 105

        error_list = self.run_checks(lot_red_ii)
        self.assertTrue(has_error(error, error_list))

    def test_ghg_reduc_sup_99(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_SUP_99

        # prepare a lot for RED II values
        lot = self.create_lot(
            delivery_date=july1st2021 + datetime.timedelta(days=15),
            ghg_reduction_red_ii=95,
            ghg_reduction=105,  # put a wrong RED I value to confirm it will be ignored
        )

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.ghg_reduction_red_ii = 99.9

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_ghg_reduc_inf_50(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_INF_50

        # prepare a lot for RED II values
        lot = self.create_lot(
            delivery_date=july1st2021 + datetime.timedelta(days=15),
            ghg_reduction_red_ii=95,
            ghg_reduction=105,  # put a wrong RED I value to confirm it will be ignored
        )

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.ghg_reduction_red_ii = 5

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_ghg_etd_0(self):
        error = CarbureSanityCheckErrors.GHG_ETD_0

        lot = self.create_lot(etd=1)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.etd = -1

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_ghg_ep_0(self):
        error = CarbureSanityCheckErrors.GHG_EP_0

        lot = self.create_lot(ep=1)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.ep = -1

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_ghg_el_neg(self):
        error = CarbureSanityCheckErrors.GHG_EL_NEG

        lot = self.create_lot(el=1)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.el = -1

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_ghg_eec_0(self):
        error = CarbureSanityCheckErrors.GHG_EEC_0

        conv_feedstock = MatierePremiere.objects.filter(category="CONV").first()
        other_feedstock = MatierePremiere.objects.exclude(category="CONV").first()

        lot = self.create_lot(eec=0, feedstock=other_feedstock)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.eec = 1
        lot.feedstock = conv_feedstock

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.eec = 0

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def test_eec_with_residue(self):
        error = CarbureSanityCheckErrors.EEC_WITH_RESIDUE

        conv_feedstock = MatierePremiere.objects.filter(category="CONV").exclude(code="EP2").first()
        other_feedstock = MatierePremiere.objects.exclude(category="CONV", code="EP2").first()
        ep2 = MatierePremiere.objects.get(code="EP2")

        lot = self.create_lot(feedstock=other_feedstock, eec=1)

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.eec = 0

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.eec = 1
        lot.feedstock = conv_feedstock

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.eec = 1
        lot.feedstock = ep2

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_ghg_reduc_inf_60(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_INF_60

        lot = self.create_lot(production_site_commissioning_date=None)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.production_site_commissioning_date = oct2015 + datetime.timedelta(days=15)
        lot.ghg_reduction_red_ii = 61

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.ghg_reduction_red_ii = 59

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

    def x_test_ghg_reduc_inf_65(self):
        error = CarbureSanityCheckErrors.GHG_REDUC_INF_65

        lot = self.create_lot(production_site_commissioning_date=None)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.production_site_commissioning_date = jan2021 + datetime.timedelta(days=15)
        lot.ghg_reduction_red_ii = 64

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.ghg_reduction_red_ii = 66

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

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

    def test_unknown_prodsite_cert(self):
        error = CarbureCertificatesErrors.UNKNOWN_PRODSITE_CERT

        lot = self.create_lot(production_site_certificate="RANDOM")

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        self.prefetched_data["certificates"]["RANDOM"] = {"valid_until": datetime.date.today()}

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_expired_prodsite_cert(self):
        error = CarbureCertificatesErrors.EXPIRED_PRODSITE_CERT

        lot = self.create_lot()

        expired_cert = {"valid_until": lot.delivery_date - datetime.timedelta(days=15)}
        valid_cert = {"valid_until": lot.delivery_date + datetime.timedelta(days=15)}

        self.prefetched_data["certificates"]["EXPIRED_CERT"] = expired_cert
        self.prefetched_data["certificates"]["VALID_CERT"] = valid_cert

        lot.production_site_certificate = "EXPIRED_CERT"

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.production_site_certificate = "VALID_CERT"

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_no_supplier_cert(self):
        error = CarbureCertificatesErrors.NO_SUPPLIER_CERT

        lot = self.create_lot(supplier_certificate="")

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.supplier_certificate = "RANDOM"

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_unknown_supplier_cert(self):
        error = CarbureCertificatesErrors.UNKNOWN_SUPPLIER_CERT

        lot = self.create_lot(supplier_certificate="RANDOM")

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        self.prefetched_data["certificates"]["RANDOM"] = {"valid_until": datetime.date.today()}

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def test_expired_supplier_cert(self):
        error = CarbureCertificatesErrors.EXPIRED_SUPPLIER_CERT

        lot = self.create_lot()

        expired_cert = {"valid_until": lot.delivery_date - datetime.timedelta(days=15)}
        valid_cert = {"valid_until": lot.delivery_date + datetime.timedelta(days=15)}

        self.prefetched_data["certificates"]["EXPIRED_CERT"] = expired_cert
        self.prefetched_data["certificates"]["VALID_CERT"] = valid_cert

        lot.supplier_certificate = "EXPIRED_CERT"

        error_list = self.run_checks(lot)
        self.assertTrue(has_error(error, error_list))

        lot.supplier_certificate = "VALID_CERT"

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

    def x_test_rejected_supplier_certificate(self):
        error = CarbureCertificatesErrors.REJECTED_SUPPLIER_CERTIFICATE
        pass

    def x_test_unknown_double_counting_certificate(self):
        error = CarbureCertificatesErrors.UNKNOWN_DOUBLE_COUNTING_CERTIFICATE

    def x_test_expired_double_counting_certificate(self):
        error = CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE

    def x_test_invalid_double_counting_certificate(self):
        error = CarbureCertificatesErrors.INVALID_DOUBLE_COUNTING_CERTIFICATE

    def x_test_missing_supplier_certificate(self):
        error = CarbureCertificatesErrors.MISSING_SUPPLIER_CERTIFICATE

    def test_etd_anormal_high(self):
        error = CarbureMLGHGErrors.ETD_ANORMAL_HIGH

        etd = ETDStats.objects.first()
        lot = self.create_lot(feedstock=etd.feedstock, etd=1)

        error_list = self.run_checks(lot)
        self.assertFalse(has_error(error, error_list))

        lot.etd = max(2 * etd.default_value, 5) + 1
        error_list = self.run_checks(lot)

        self.assertTrue(has_error(error, error_list))

    def test_etd_no_eu_too_low(self):
        error = CarbureMLGHGErrors.ETD_NO_EU_TOO_LOW

    def x_test_etd_eu_default_value(self):
        error = CarbureMLGHGErrors.ETD_EU_DEFAULT_VALUE

    def x_test_eec_anormal_low(self):
        error = CarbureMLGHGErrors.EEC_ANORMAL_LOW

    def x_test_eec_anormal_high(self):
        error = CarbureMLGHGErrors.EEC_ANORMAL_HIGH

    def x_test_ep_anormal_low(self):
        error = CarbureMLGHGErrors.EP_ANORMAL_LOW

    def x_test_ep_anormal_high(self):
        error = CarbureMLGHGErrors.EP_ANORMAL_HIGH

    def x_test_incorrect_format_delivery_date(self):
        error = "INCORRECT_FORMAT_DELIVERY_DATE"

    def x_test_could_not_find_production_site(self):
        error = "COULD_NOT_FIND_PRODUCTION_SITE"

    def x_test_missing_biofuel(self):
        error = "MISSING_BIOFUEL"

    def x_test_unknown_biofuel(self):
        error = "UNKNOWN_BIOFUEL"

    def x_test_missing_feedstock(self):
        error = "MISSING_FEEDSTOCK"

    def x_test_unknown_feedstock(self):
        error = "UNKNOWN_FEEDSTOCK"

    def x_test_missing_country_of_origin(self):
        error = "MISSING_COUNTRY_OF_ORIGIN"

    def x_test_unknown_country_of_origin(self):
        error = "UNKNOWN_COUNTRY_OF_ORIGIN"

    def x_test_carburestockerrors(self):
        error = "CarbureStockErrors"

    def x_test_volume_format_incorrect(self):
        error = "VOLUME_FORMAT_INCORRECT"

    def x_test_wrong_float_format(self):
        error = "WRONG_FLOAT_FORMAT"

    def x_test_wrong_float_format(self):
        error = "WRONG_FLOAT_FORMAT"

    def x_test_unknown_delivery_site(self):
        error = "UNKNOWN_DELIVERY_SITE"

    def x_test_unknown_client(self):
        error = "UNKNOWN_CLIENT"


def has_error(error, error_list):
    for e in error_list:
        if e.error == error:
            return True
    return False


def enrich_lot(lot):
    queryset = CarbureLot.objects.filter(id=lot.id).select_related(
        "carbure_producer",
        "carbure_supplier",
        "carbure_client",
        "added_by",
        "carbure_production_site",
        "carbure_production_site__producer",
        "carbure_production_site__country",
        "production_country",
        "carbure_dispatch_site",
        "carbure_dispatch_site__country",
        "dispatch_site_country",
        "carbure_delivery_site",
        "carbure_delivery_site__country",
        "delivery_site_country",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "parent_stock",
        "parent_lot",
    )
    return queryset.first()
