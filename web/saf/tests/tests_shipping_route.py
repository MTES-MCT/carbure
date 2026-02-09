from django.test import override_settings

from saf.factories.saf_logistics import SafLogisticsFactory
from saf.models.saf_logistics import SafLogistics
from saf.services.is_shipping_route_available import is_shipping_route_available
from saf.tests import TestCase
from transactions.factories.site import SiteFactory
from transactions.models.site import Site


class SafShippingRoutesTest(TestCase):
    def setUp(self):
        super().setUp()

        self.origin_depot = SiteFactory.create(site_type=Site.EFCA)
        self.destination_airport = SiteFactory.create(site_type=Site.AIRPORT)

        self.not_regsitered_depot = SiteFactory.create(site_type=Site.EFCA)
        self.not_registered_airport = SiteFactory.create(site_type=Site.AIRPORT)

        SafLogisticsFactory.create(
            origin_depot=self.origin_depot,
            destination_airport=self.destination_airport,
            shipping_method=SafLogistics.PIPELINE_LHP,
            has_intermediary_depot=False,
        )

    def test_pass_if_route_is_registered(self):
        self.assertTrue(
            is_shipping_route_available(
                origin_depot=self.origin_depot,
                destination_airport=self.destination_airport,
                shipping_method=SafLogistics.PIPELINE_LHP,
                has_intermediary_depot=False,
            )
        )

    def test_fail_if_route_is_not_registered(self):
        self.assertFalse(
            is_shipping_route_available(
                origin_depot=self.origin_depot,
                destination_airport=self.destination_airport,
                shipping_method=SafLogistics.TRAIN,
                has_intermediary_depot=False,
            )
        )

        self.assertFalse(
            is_shipping_route_available(
                origin_depot=self.not_regsitered_depot,
                destination_airport=self.destination_airport,
                shipping_method=SafLogistics.PIPELINE_LHP,
                has_intermediary_depot=False,
            )
        )

        self.assertFalse(
            is_shipping_route_available(
                origin_depot=self.origin_depot,
                destination_airport=self.not_registered_airport,
                shipping_method=SafLogistics.PIPELINE_LHP,
                has_intermediary_depot=False,
            )
        )

        self.assertFalse(
            is_shipping_route_available(
                origin_depot=self.origin_depot,
                destination_airport=self.destination_airport,
                shipping_method=SafLogistics.TRAIN,
                has_intermediary_depot=True,
            )
        )

    def test_pass_if_airport_is_missing(self):
        # the goal is to deal with tickets that aren't sent to actual airlines
        # when tickets are exchanged between operators only, there's no need for a destination airport

        self.assertTrue(
            is_shipping_route_available(
                origin_depot=self.origin_depot,
                destination_airport=None,
                shipping_method=None,
                has_intermediary_depot=None,
            )
        )

    def test_always_pass_if_using_truck(self):
        # trucks are a special case as they have no physical limitation to where they can go
        # so technically, any route that uses trucks for transport should always pass validation

        self.assertTrue(
            is_shipping_route_available(
                origin_depot=self.not_regsitered_depot,
                destination_airport=self.not_registered_airport,
                shipping_method=SafLogistics.TRUCK,
                has_intermediary_depot=True,
            )
        )

    @override_settings(ENABLE_SAF_LOGISTICS=False)
    def test_skip_logistics_validation_with_feature_flag(self):
        self.assertTrue(
            is_shipping_route_available(
                origin_depot=self.origin_depot,
                destination_airport=self.destination_airport,
                shipping_method=SafLogistics.TRAIN,
                has_intermediary_depot=False,
            )
        )
