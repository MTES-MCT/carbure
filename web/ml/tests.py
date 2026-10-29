from datetime import date
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.apps import apps
from django.db import connection
from django.test import SimpleTestCase, TestCase

from core.models import GenericError
from ml.scripts.calc_ml_score import calc_ml_score


class CalcMLScoreTest(SimpleTestCase):
    def score_lot(self, eec, ep, config=None):
        lot = SimpleNamespace(
            feedstock=SimpleNamespace(code="COLZA"),
            country_of_origin=SimpleNamespace(code_pays="FR"),
            biofuel=SimpleNamespace(code="EMHV"),
            eec=eec,
            ep=ep,
            ml_scoring=1.0,
            ml_control_requested=True,
            save=Mock(),
        )
        data = {
            "eec": {"COLZAFR": SimpleNamespace(default_value=10.0, average=10.0)},
            "ep": {"COLZAEMHV": SimpleNamespace(average=20.0, default_value_max_ep=20.0)},
        }
        with (
            patch("ml.scripts.calc_ml_score.get_prefetched_data", return_value=data),
            patch("ml.scripts.calc_ml_score.CarbureLot.objects.select_related") as select_related,
            patch("ml.scripts.calc_ml_score.tqdm", side_effect=lambda lots: lots),
        ):
            select_related.return_value.filter.return_value.iterator.return_value = [lot]
            calc_ml_score(config=config)

        lot.save.assert_called_once_with()
        return lot

    def test_high_emissions_clear_previous_score_and_control_request(self):
        for eec, ep in [(30.0, 20.0), (10.0, 50.0), (30.0, 50.0)]:
            with self.subTest(eec=eec, ep=ep):
                lot = self.score_lot(eec, ep)

                self.assertEqual(lot.ml_scoring, 0)
                self.assertFalse(lot.ml_control_requested)

    def test_low_emissions_still_request_control(self):
        for eec, ep, expected_score in [(5.0, 20.0, 0.25), (10.0, 10.0, 0.25), (5.0, 10.0, 0.5)]:
            with self.subTest(eec=eec, ep=ep):
                lot = self.score_lot(eec, ep)

                self.assertAlmostEqual(lot.ml_scoring, expected_score)
                self.assertTrue(lot.ml_control_requested)

    def test_emission_thresholds_can_be_configured_independently(self):
        configs = [
            ({"eec_threshold": 0.7}, 0.0625),
            ({"ep_threshold": 0.7}, 0.0625),
            ({"eec_threshold": 0.7, "ep_threshold": 0.7}, 0.0),
        ]
        for config, expected_score in configs:
            with self.subTest(config=config):
                lot = self.score_lot(7.5, 15.0, config=config)

                self.assertAlmostEqual(lot.ml_scoring, expected_score)

    def test_emission_exponents_can_be_configured_independently(self):
        config = {"eec_exponent": 1, "ep_exponent": 3}

        lot = self.score_lot(5.0, 10.0, config=config)

        self.assertAlmostEqual(lot.ml_scoring, 0.625)

    def test_control_threshold_does_not_change_the_score(self):
        for threshold, expected_control in [(0.2, True), (0.25, False), (0.3, False)]:
            with self.subTest(threshold=threshold):
                lot = self.score_lot(5.0, 20.0, config={"control_threshold": threshold})

                self.assertAlmostEqual(lot.ml_scoring, 0.25)
                self.assertEqual(lot.ml_control_requested, expected_control)

    def test_lookback_uses_the_current_date_on_each_call(self):
        config = {"lookback_days": 30}
        with (
            patch("ml.scripts.calc_ml_score.datetime.date") as current_date,
            patch("ml.scripts.calc_ml_score.get_prefetched_data", return_value={"eec": {}, "ep": {}}),
            patch("ml.scripts.calc_ml_score.CarbureLot.objects.select_related") as select_related,
            patch("ml.scripts.calc_ml_score.tqdm", side_effect=lambda lots: lots),
        ):
            current_date.today.side_effect = [date(2026, 1, 31), date(2026, 2, 28)]
            select_related.return_value.filter.return_value.iterator.return_value = []

            calc_ml_score(config=config)
            calc_ml_score(config=config)

            filters = select_related.return_value.filter.call_args_list
            self.assertEqual(filters[0].kwargs["created_at__gt"], date(2026, 1, 1))
            self.assertEqual(filters[1].kwargs["created_at__gt"], date(2026, 1, 29))


class RemoveETDReferenceErrorsTest(TestCase):
    def test_cleanup_preserves_other_errors_including_etd_model_detections(self):
        retired_errors = ["ETD_NO_EU_TOO_LOW", "ETD_EU_DEFAULT_VALUE", "ETD_ANORMAL_HIGH", "ETD_HIGHER_THAN_DEFAULT"]
        preserved_errors = [
            "GHG_ETD_0",
            "IF_OUTLIER_ETD",
            "LOF_OUTLIER_ETD",
            "OUTLIER_EEC",
            "OUTLIER_EP",
            "OUTLIER_ETD",
        ]
        GenericError.objects.bulk_create([GenericError(error=error) for error in retired_errors + preserved_errors])
        migration = import_module("ml.migrations.0002_remove_etd_stats")

        migration.remove_etd_reference_errors(apps, SimpleNamespace(connection=connection))

        self.assertCountEqual(GenericError.objects.values_list("error", flat=True), preserved_errors)
