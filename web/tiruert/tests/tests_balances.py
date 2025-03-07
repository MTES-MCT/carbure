from django.urls import reverse

from tiruert.models.operation import Operation
from tiruert.tests import TestCase


class TiruertBalancesTest(TestCase):
    def setUp(self):
        super().setUp()

        operations = Operation.objects.all()
        operations.update(status=Operation.ACCEPTED)

    def test_view_balances(self):
        query = {
            "entity_id": self.entity.id,
        }

        expected_response = [
            {
                "sector": "ESSENCE",
                "customs_category": "CONV",
                "biofuel": {"id": 33, "code": "ETH"},
                "initial_balance": 0.0,
                "available_balance": 10000.0,
                "final_balance": 10000.0,
                "quantity": {"credit": 10000.0, "debit": 0.0},
                "teneur": 0.0,
                "pending": 0,
                "unit": "l",
            },
            {
                "sector": "DIESEL",
                "customs_category": "ANN-IX-A",
                "biofuel": {"id": 31, "code": "EMAG"},
                "initial_balance": 0.0,
                "available_balance": 5000.0,
                "final_balance": 5000.0,
                "quantity": {"credit": 5000.0, "debit": 0.0},
                "teneur": 0.0,
                "pending": 0,
                "unit": "l",
            },
        ]

        response = self.client.get(reverse("operations-balance"), query)
        data = response.json()
        assert response.status_code == 200
        assert data["count"] == 2
        assert data["results"] == expected_response

    def test_view_balances_by_sector(self):
        query = {
            "entity_id": self.entity.id,
            "group_by": "sector",
        }

        expected_response = [
            {
                "sector": "ESSENCE",
                "initial_balance": 0.0,
                "available_balance": 10000.0,
                "final_balance": 10000.0,
                "quantity": {"credit": 10000.0, "debit": 0.0},
                "teneur": 0.0,
                "pending": 0,
                "unit": "l",
            },
            {
                "sector": "DIESEL",
                "initial_balance": 0.0,
                "available_balance": 5000.0,
                "final_balance": 5000.0,
                "quantity": {"credit": 5000.0, "debit": 0.0},
                "teneur": 0.0,
                "pending": 0,
                "unit": "l",
            },
        ]

        response = self.client.get(reverse("operations-balance"), query)
        assert response.status_code == 200
        assert response.json()["count"] == 2
        data = response.json()["results"]
        assert data == expected_response

    def test_view_balances_by_lot(self):
        query = {
            "entity_id": self.entity.id,
            "group_by": "lot",
        }

        response = self.client.get(reverse("operations-balance"), query)
        assert response.status_code == 200
        assert response.json()["count"] == 2
        data = response.json()["results"]
        assert list(data[0].keys()) == ["customs_category", "biofuel", "lots"]
        assert list(data[0]["lots"][0].keys()) == ["lot", "volume", "emission_rate_per_mj"]
        assert len(data[0]["lots"]) == 4
        assert len(data[1]["lots"]) == 1

    def test_view_balances_wrong_entity(self):
        query = {
            "entity_id": 9999,
        }

        response = self.client.get(reverse("operations-balance"), query)
        assert response.status_code == 403

    def test_view_balances_simulate_min_max_success(self):
        query = {
            "entity_id": self.entity.id,
            "biofuel": 33,
            "customs_category": "CONV",
            "debited_entity": self.entity.id,
            "target_volume": 1000,
        }

        response = self.client.post(reverse("operations-simulate-min-max"), query)
        assert response.status_code == 200
        data = response.json()
        assert data["min_avoided_emissions"] == 1.8732
        assert data["max_avoided_emissions"] == 1.9467

    def test_view_balances_simulate_min_max_insufficient_volume(self):
        query = {
            "entity_id": self.entity.id,
            "biofuel": 33,
            "customs_category": "CONV",
            "debited_entity": self.entity.id,
            "target_volume": 100000,
        }

        response = self.client.post(reverse("operations-simulate-min-max"), query)
        assert response.status_code == 400
        data = response.json()
        assert data == {"error": "INSUFFICIENT_INPUT_VOLUME"}

    def test_view_balances_simulate_success(self):
        query = {
            "entity_id": self.entity.id,
            "biofuel": 33,
            "customs_category": "CONV",
            "debited_entity": self.entity.id,
            "target_volume": 1000,
            "target_emission": 1.9,
        }

        response = self.client.post(reverse("operations-simulate"), query)
        assert response.status_code == 200
        data = response.json()
        print(data)
        assert len(data) == 2
        assert list(data.keys()) == ["selected_lots", "fun"]
        assert len(data["selected_lots"]) == 2
        assert list(data["selected_lots"][0].keys()) == ["lot_id", "volume", "emission_rate_per_mj"]

    def test_view_balances_simulate_no_results(self):
        query = {
            "entity_id": self.entity.id,
            "biofuel": 33,
            "customs_category": "CONV",
            "debited_entity": self.entity.id,
            "target_volume": 1000,
            "target_emission": 2,
        }

        response = self.client.post(reverse("operations-simulate"), query)
        assert response.status_code == 400
        data = response.json()
        assert data == {"error": "NO_SUITABLE_LOTS_FOUND"}
