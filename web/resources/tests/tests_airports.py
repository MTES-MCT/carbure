from django.test import TestCase
from django.urls import reverse

from core.tests_utils import setup_current_user
from saf.factories.saf_logistics import SafLogisticsFactory
from saf.models.saf_logistics import SafLogistics
from transactions.factories.site import SiteFactory
from transactions.models.site import Site


class AirportTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo")

        self.depot_a = SiteFactory.create(site_type=Site.EFPE)
        self.depot_b = SiteFactory.create(site_type=Site.EFS)

        self.airport_a = SiteFactory.create(
            name="Aéroport Paris",
            private=True,
            site_type=Site.AIRPORT,
        )
        self.airport_b = SiteFactory.create(
            name="Aéroport Marseille",
            private=False,
            site_type=Site.AIRPORT,
        )

    def get_airports(
        self,
        query=None,
        public_only=None,
        origin_depot=None,
        shipping_method=None,
        has_intermediary_depot=None,
    ):
        query_params = {}
        if query:
            query_params["query"] = query
        if public_only:
            query_params["public_only"] = public_only
        if origin_depot:
            query_params["origin_depot_id"] = origin_depot.id
        if shipping_method:
            query_params["shipping_method"] = shipping_method
        if has_intermediary_depot is not None:
            query_params["has_intermediary_depot"] = has_intermediary_depot

        response = self.client.get(reverse("resources-airports"), query_params=query_params)
        data = response.json()
        return [a["name"] for a in data]

    def test_list_all_airpots(self):
        data = self.get_airports()
        self.assertCountEqual(data, ["Aéroport Paris", "Aéroport Marseille"])

    def test_list_public_airpots(self):
        data = self.get_airports(public_only=True)
        self.assertCountEqual(data, ["Aéroport Marseille"])

    def test_list_airpots_for_depot_and_shipping_method(self):
        SafLogisticsFactory.create(
            origin_depot=self.depot_a,
            destination_airport=self.airport_a,
            shipping_method=SafLogistics.TRAIN,
            has_intermediary_depot=False,
        )
        SafLogisticsFactory.create(
            origin_depot=self.depot_a,
            destination_airport=self.airport_a,
            shipping_method=SafLogistics.BARGE,
            has_intermediary_depot=True,
        )
        SafLogisticsFactory.create(
            origin_depot=self.depot_a,
            destination_airport=self.airport_a,
            shipping_method=SafLogistics.TRUCK,
            has_intermediary_depot=True,
        )

        # partial queries return nothing
        data = self.get_airports(origin_depot=self.depot_a)
        self.assertCountEqual(data, [])
        data = self.get_airports(shipping_method=SafLogistics.TRAIN)
        self.assertCountEqual(data, [])
        data = self.get_airports(has_intermediary_depot=True)
        self.assertCountEqual(data, [])

        # queries for shipping_method=TRUCK always return all airports, ignoring defined routes
        data = self.get_airports(origin_depot=self.depot_a, shipping_method=SafLogistics.TRUCK, has_intermediary_depot=False)
        self.assertCountEqual(data, ["Aéroport Paris", "Aéroport Marseille"])

        data = self.get_airports(origin_depot=self.depot_a, shipping_method=SafLogistics.TRAIN, has_intermediary_depot=False)
        self.assertCountEqual(data, ["Aéroport Paris"])
        data = self.get_airports(origin_depot=self.depot_a, shipping_method=SafLogistics.BARGE, has_intermediary_depot=True)
        self.assertCountEqual(data, ["Aéroport Paris"])
