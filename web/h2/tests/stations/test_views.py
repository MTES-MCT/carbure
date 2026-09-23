from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity, ExternalAdminRights, Pays
from core.tests_utils import setup_current_user
from h2.factories import H2StationFactory
from h2.models import H2Station
from transactions.models.site import Site


class H2StationViewsTests(TestCase):
    def setUp(self):
        self.hrs_entity = Entity.objects.create(
            name="Test HRS",
            entity_type=Entity.HRS,
        )
        self.other_hrs = Entity.objects.create(
            name="Other HRS",
            entity_type=Entity.HRS,
        )
        self.h2_admin = Entity.objects.create(
            name="H2 Admin",
            entity_type=Entity.EXTERNAL_ADMIN,
        )
        ExternalAdminRights.objects.create(entity=self.h2_admin, right=ExternalAdminRights.H2)
        self.country = Pays.objects.create(code_pays="FR", name="France", name_en="France")

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.hrs_entity, "RW")],
        )

        self.list_url = reverse("h2-station-list")
        self.base_params = {"entity_id": self.hrs_entity.id}

    def _station_payload(self, **overrides):
        data = {
            "name": "Station H2 Test",
            "address": "1 rue de la Pompe",
            "postal_code": "75001",
            "city": "Paris",
            "country": self.country.pk,
            "access_type": H2Station.PUBLIC,
            "distributed_pressure": [H2Station.DP_350_BAR, H2Station.DP_700_BAR],
            "has_personal_vehicle_connector": True,
            "has_compliant_measuring_instruments": True,
            "storage_capacity": 1000,
            "distribution_capacity": 500,
            "site_siret": "12345678900012",
            "commissioning_date": "2024-01-15",
        }
        data.update(overrides)
        return data

    def test_list_stations(self):
        H2StationFactory.create(name="Mine", created_by=self.hrs_entity, country=self.country)
        H2StationFactory.create(name="Other", created_by=self.other_hrs, country=self.country)

        response = self.client.get(self.list_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Mine")

    def test_create_station(self):
        response = self.client.post(
            self.list_url,
            self._station_payload(),
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        station = H2Station.objects.get(created_by=self.hrs_entity)
        self.assertEqual(station.name, "Station H2 Test")
        self.assertEqual(station.site_type, Site.H2_REFUELING_STATION)
        self.assertEqual(station.created_by, self.hrs_entity)
        self.assertEqual(station.distributed_pressure, [H2Station.DP_350_BAR, H2Station.DP_700_BAR])
        self.assertTrue(station.has_personal_vehicle_connector)
        self.assertTrue(station.has_compliant_measuring_instruments)

    def test_retrieve_station(self):
        station = H2StationFactory.create(created_by=self.hrs_entity, country=self.country)
        detail_url = reverse("h2-station-detail", kwargs={"pk": station.pk})

        response = self.client.get(detail_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], station.pk)
        self.assertEqual(response.data["distributed_pressure"], [H2Station.DP_350_BAR])

    def test_update_station(self):
        station = H2StationFactory.create(created_by=self.hrs_entity, country=self.country)
        detail_url = reverse("h2-station-detail", kwargs={"pk": station.pk})

        response = self.client.put(
            detail_url,
            self._station_payload(
                name="Station Updated",
                distributed_pressure=[H2Station.DP_700_BAR],
                storage_capacity=2000,
                has_compliant_measuring_instruments=False,
            ),
            content_type="application/json",
            query_params=self.base_params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        station.refresh_from_db()
        self.assertEqual(station.name, "Station Updated")
        self.assertEqual(station.distributed_pressure, [H2Station.DP_700_BAR])
        self.assertEqual(station.storage_capacity, 2000)
        self.assertFalse(station.has_compliant_measuring_instruments)

    def test_cannot_retrieve_other_entity_station(self):
        station = H2StationFactory.create(created_by=self.other_hrs, country=self.country)
        detail_url = reverse("h2-station-detail", kwargs={"pk": station.pk})

        response = self.client.get(detail_url, self.base_params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _login_as_h2_admin(self):
        setup_current_user(
            self,
            "admin@carbure.local",
            "Admin",
            "gogogo",
            [(self.h2_admin, "RW")],
        )

    def test_admin_lists_all_hrs_stations(self):
        self._login_as_h2_admin()
        H2StationFactory.create(name="Mine", created_by=self.hrs_entity, country=self.country)
        H2StationFactory.create(name="Other", created_by=self.other_hrs, country=self.country)

        response = self.client.get(self.list_url, {"entity_id": self.h2_admin.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertCountEqual([station["name"] for station in response.data["results"]], ["Mine", "Other"])
        self.assertCountEqual(
            [station["entity_name"] for station in response.data["results"]],
            [self.hrs_entity.name, self.other_hrs.name],
        )

    def test_admin_filters_stations_by_entity(self):
        self._login_as_h2_admin()
        H2StationFactory.create(name="Mine", created_by=self.hrs_entity, country=self.country)
        H2StationFactory.create(name="Other", created_by=self.other_hrs, country=self.country)

        response = self.client.get(
            self.list_url,
            {"entity_id": self.h2_admin.id, "entity": self.hrs_entity.name},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Mine")
        self.assertEqual(response.data["results"][0]["entity_name"], self.hrs_entity.name)

    def test_hrs_entity_filter_stays_scoped_to_own_stations(self):
        H2StationFactory.create(name="Mine", created_by=self.hrs_entity, country=self.country)
        H2StationFactory.create(name="Other", created_by=self.other_hrs, country=self.country)

        response = self.client.get(self.list_url, {**self.base_params, "entity": self.other_hrs.name})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_entity_filter_options_stay_scoped(self):
        H2StationFactory.create(name="Mine", created_by=self.hrs_entity, country=self.country)
        H2StationFactory.create(name="Other", created_by=self.other_hrs, country=self.country)
        filters_url = reverse("h2-station-filters")

        hrs_response = self.client.get(filters_url, {**self.base_params, "filter": "entity"})

        self.assertEqual(hrs_response.status_code, status.HTTP_200_OK)
        self.assertEqual(hrs_response.data, [self.hrs_entity.name])

        self._login_as_h2_admin()
        admin_response = self.client.get(filters_url, {"entity_id": self.h2_admin.id, "filter": "entity"})

        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(admin_response.data, [self.hrs_entity.name, self.other_hrs.name])

    def test_admin_retrieves_any_hrs_station(self):
        self._login_as_h2_admin()
        station = H2StationFactory.create(created_by=self.other_hrs, country=self.country)
        detail_url = reverse("h2-station-detail", kwargs={"pk": station.pk})

        response = self.client.get(detail_url, {"entity_id": self.h2_admin.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], station.pk)

    def test_admin_cannot_write_stations(self):
        self._login_as_h2_admin()
        station = H2StationFactory.create(created_by=self.hrs_entity, country=self.country)
        detail_url = reverse("h2-station-detail", kwargs={"pk": station.pk})
        admin_params = {"entity_id": self.h2_admin.id}

        create_response = self.client.post(
            self.list_url,
            self._station_payload(),
            content_type="application/json",
            query_params=admin_params,
        )
        update_response = self.client.put(
            detail_url,
            self._station_payload(name="Station Updated"),
            content_type="application/json",
            query_params=admin_params,
        )
        delete_response = self.client.delete(detail_url, query_params=admin_params)

        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        station.refresh_from_db()
        self.assertNotEqual(station.name, "Station Updated")
