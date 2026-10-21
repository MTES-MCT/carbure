from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from ml.scripts.calc_ml_score import calc_ml_score


class CalcMLScoreTest(SimpleTestCase):
    def score_lot(self, eec, ep):
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
            "etd": {},
        }
        with (
            patch("ml.scripts.calc_ml_score.get_prefetched_data", return_value=data),
            patch("ml.scripts.calc_ml_score.CarbureLot.objects.select_related") as select_related,
            patch("ml.scripts.calc_ml_score.tqdm", side_effect=lambda lots: lots),
        ):
            select_related.return_value.filter.return_value.iterator.return_value = [lot]
            calc_ml_score()

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
