from django.test import TestCase

from tiruert.models.operation import Operation
from tiruert.services import operation_year as operation_year_service


class OperationYearTest(TestCase):
    def test_resolve_credit_type_from_durability_period(self):
        self.assertEqual(
            operation_year_service.resolve(Operation.INCORPORATION, "202403", 2025),
            2024,
        )
        self.assertEqual(
            operation_year_service.resolve(Operation.MAC_BIO, "202312", None),
            2023,
        )

    def test_resolve_credit_type_without_durability_period_falls_back_to_declaration_year(self):
        self.assertEqual(
            operation_year_service.resolve(Operation.INCORPORATION, None, 2025),
            2025,
        )

    def test_resolve_other_types_use_declaration_year(self):
        self.assertEqual(
            operation_year_service.resolve(Operation.TENEUR, "202403", 2025),
            2025,
        )

    def test_year_property_delegates_to_service(self):
        operation = Operation(
            type=Operation.MAC_BIO,
            durability_period="202406",
            declaration_year=2025,
        )
        self.assertEqual(operation.year, 2024)
