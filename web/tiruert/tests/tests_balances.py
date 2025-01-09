from django.urls import reverse

from tiruert.tests import TestCase


class TiruertBalancesTest(TestCase):
    def setUp(self):
        super().setUp()

    def test_view_balances(self):
        query = {
            "entity_id": self.entity.id,
        }

        expected_response = [
            {
                "sector": "ESSENCE",
                "customs_category": "CONV",
                "biofuel": "ETH",
                "initial_balance": "0.00",
                "available_balance": "10000.00",
                "final_balance": "10000.00",
                "volume": {"credit": "10000.00", "debit": "0.00"},
                "teneur": "0.00",
                "pending": 0,
            },
            {
                "sector": "DIESEL",
                "customs_category": "ANN-IX-A",
                "biofuel": "EMAG",
                "initial_balance": "0.00",
                "available_balance": "5000.00",
                "final_balance": "5000.00",
                "volume": {"credit": "5000.00", "debit": "0.00"},
                "teneur": "0.00",
                "pending": 0,
            },
        ]

        response = self.client.get(reverse("operations-balance"), query)
        data = response.json()
        assert response.status_code == 200
        assert len(data) == 2
        assert data == expected_response

    def test_view_balances_by_sector(self):
        query = {
            "entity_id": self.entity.id,
            "group_by": "sector",
        }

        expected_response = [
            {
                "sector": "ESSENCE",
                "initial_balance": "0.00",
                "available_balance": "10000.00",
                "final_balance": "10000.00",
                "volume": {"credit": "10000.00", "debit": "0.00"},
                "teneur": "0.00",
                "pending": 0,
            },
            {
                "sector": "DIESEL",
                "initial_balance": "0.00",
                "available_balance": "5000.00",
                "final_balance": "5000.00",
                "volume": {"credit": "5000.00", "debit": "0.00"},
                "teneur": "0.00",
                "pending": 0,
            },
        ]

        response = self.client.get(reverse("operations-balance"), query)
        data = response.json()
        assert response.status_code == 200
        assert len(data) == 2
        assert data == expected_response

    def test_view_balances_by_lot(self):
        query = {
            "entity_id": self.entity.id,
            "group_by": "lot",
        }

        response = self.client.get(reverse("operations-balance"), query)
        data = response.json()
        assert response.status_code == 200
        assert len(data) == 2
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
        assert data["blending_min_emission_rate_per_mj"] == 1.3
        assert data["blending_max_emission_rate_per_mj"] == 4.8

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
        assert data == ["INSUFFICIENT_INPUT_VOLUME"]

    def test_view_balances_simulate_success(self):
        query = {
            "entity_id": self.entity.id,
            "biofuel": 33,
            "customs_category": "CONV",
            "debited_entity": self.entity.id,
            "target_volume": 1000,
            "target_emission": 2,
        }

        response = self.client.post(reverse("operations-simulate"), query)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert list(data[0].keys()) == ["lot_id", "volume", "emission_rate_per_mj", "fun"]

    def test_view_balances_simulate_no_results(self):
        query = {
            "entity_id": self.entity.id,
            "biofuel": 33,
            "customs_category": "CONV",
            "debited_entity": self.entity.id,
            "target_volume": 1000,
            "target_emission": 0.5,
        }

        response = self.client.post(reverse("operations-simulate"), query)
        assert response.status_code == 400
        data = response.json()
        assert data == ["NO_SUITABLE_LOTS_FOUND"]
