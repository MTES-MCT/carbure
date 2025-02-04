from django.urls import reverse
from django.utils import timezone

from tiruert.models.operation import Operation
from tiruert.tests import TestCase


class TiruertOperationsTest(TestCase):
    def setUp(self):
        super().setUp()

    def test_create_tiruert_operations_from_lots(self):
        operations = Operation.objects.all()
        assert operations.count() == 4

        operation_details = Operation.objects.first().details.all()
        assert operation_details.count() == 2

    def test_view_operations(self):
        query = {
            "entity_id": self.entity.id,
            "date_from": timezone.now().strftime("%Y-%m-%d"),
        }
        response = self.client.get(reverse("operations-list"), query)
        assert response.status_code == 200
        assert response.json()["count"] == 4
        data = response.json()["results"]
        assert list(data[0].keys()) == [
            "id",
            "type",
            "status",
            "sector",
            "customs_category",
            "biofuel",
            "credited_entity",
            "debited_entity",
            "from_depot",
            "to_depot",
            "created_at",
            "volume",
            "unit",
        ]

        query = {
            "entity_id": self.entity.id,
            "details": 1,
        }
        response = self.client.get(reverse("operations-list"), query)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["count"] == 4
        assert len(response_json["results"][0]["details"]) == 2
