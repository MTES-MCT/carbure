from django.db.models import FloatField, Value
from django.test import SimpleTestCase, TestCase

from tiruert.models import Operation
from tiruert.services.energy import (
    avoided_emissions_tco2,
    avoided_emissions_tco2_expression,
    energy_mj,
    energy_mj_expression,
    tco2_from_mj,
    tco2_from_mj_expression,
)


class EnergyServicePureFunctionsTest(SimpleTestCase):
    def test_energy_mj_uses_default_renewable_energy_share(self):
        result = energy_mj(1000, 10)

        self.assertEqual(result, 10000)

    def test_energy_mj_applies_renewable_energy_share(self):
        result = energy_mj(1000, 10, 0.5)

        self.assertEqual(result, 5000)

    def test_tco2_from_mj_converts_using_factor(self):
        result = tco2_from_mj(5000, 94)

        self.assertEqual(result, 0.47)

    def test_avoided_emissions_tco2_uses_energy_and_emission_rate(self):
        result = avoided_emissions_tco2(5000, 60, 94)

        self.assertEqual(result, 0.17)


class EnergyServiceExpressionsTest(TestCase):
    def setUp(self):
        self.operation = Operation.objects.create(type=Operation.CESSION)

    def _evaluate(self, expression):
        return (
            Operation.objects.filter(pk=self.operation.pk).annotate(value=expression).values_list("value", flat=True).get()
        )

    def test_energy_mj_expression_returns_float_expression(self):
        expression = energy_mj_expression(Value(1000.0), Value(0.5), Value(10.0))

        self.assertIsInstance(expression.output_field, FloatField)

    def test_energy_mj_expression_evaluates_expected_value(self):
        expression = energy_mj_expression(Value(1000.0), Value(0.5), Value(10.0))

        result = self._evaluate(expression)

        self.assertEqual(result, 5000.0)

    def test_energy_mj_expression_applies_sign_when_provided(self):
        expression = energy_mj_expression(Value(1000.0), Value(0.5), Value(10.0), Value(-1.0))

        result = self._evaluate(expression)

        self.assertEqual(result, -5000.0)

    def test_tco2_from_mj_expression_evaluates_expected_value(self):
        expression = tco2_from_mj_expression(Value(5000.0), 94)

        result = self._evaluate(expression)

        self.assertAlmostEqual(result, 0.47)

    def test_avoided_emissions_tco2_expression_evaluates_expected_value(self):
        energy_expression = energy_mj_expression(Value(1000.0), Value(0.5), Value(10.0))
        expression = avoided_emissions_tco2_expression(energy_expression, Value(60.0), 94)

        result = self._evaluate(expression)

        self.assertAlmostEqual(result, 0.17)
