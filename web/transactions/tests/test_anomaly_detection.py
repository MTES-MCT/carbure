from unittest.mock import Mock, patch

import pandas as pd
from django.core.exceptions import EmptyResultSet
from django.test import SimpleTestCase

from core.models import CarbureLot
from transactions.services.anomaly_detection.create_errors import create_errors
from transactions.services.anomaly_detection.detect_outliers import detect_outliers


class DetectOutliersTest(SimpleTestCase):
    def test_flags_identify_the_correct_model(self):
        data = pd.DataFrame({"ep": [1.0, 2.0, 3.0, 4.0], "group": ["group"] * 4})
        isolation_forest = Mock()
        isolation_forest.fit_predict.return_value = pd.Series([-1, 1, 1, 1])
        local_outlier_factor = Mock()
        local_outlier_factor.fit_predict.return_value = pd.Series([1, -1, 1, 1])

        outliers = detect_outliers(data, "ep", {"ep": []}, 0.75, [0.75], isolation_forest, local_outlier_factor)

        self.assertEqual(outliers["ep"].tolist(), [1.0, 2.0])
        self.assertEqual(outliers["is_if_outlier"].tolist(), [True, False])
        self.assertEqual(outliers["is_lof_outlier"].tolist(), [False, True])


class CreateAnomalyErrorsTest(SimpleTestCase):
    def setUp(self):
        self.exclude_patch = patch.object(CarbureLot.objects, "exclude")
        self.processed_lots = self.exclude_patch.start().return_value.filter.return_value
        self.addCleanup(self.exclude_patch.stop)
        self.processed_lots.filter.side_effect = self.match_lots

        self.errors_patch = patch("transactions.services.anomaly_detection.create_errors.GenericError.objects")
        self.errors = self.errors_patch.start()
        self.addCleanup(self.errors_patch.stop)

    def match_lots(self, condition):
        # Compile the actual Django predicate without executing a database query.
        try:
            CarbureLot.objects.filter(condition).query.sql_with_params()
        except EmptyResultSet:
            ids = []
        else:
            ids = [123]
        result = Mock()
        result.distinct.return_value.values_list.return_value = ids
        return result

    def test_no_outliers_does_not_flag_all_lots(self):
        outliers = pd.DataFrame(columns=["ep", "is_lof_outlier", "is_if_outlier"])

        self.assertEqual(create_errors({"ep": outliers}), [])

        self.errors.bulk_create.assert_called_once_with([], batch_size=1000)
        # Even an empty run must remove previous detections in the processed scope.
        self.errors.filter.assert_called_once_with(error__in=["LOF_OUTLIER", "IF_OUTLIER"], lot__in=self.processed_lots)
        self.errors.filter.return_value.delete.assert_called_once_with()

    def test_model_without_outliers_does_not_flag_all_lots(self):
        for flag, error in [("is_lof_outlier", "LOF_OUTLIER"), ("is_if_outlier", "IF_OUTLIER")]:
            with self.subTest(model=flag):
                self.errors.reset_mock()
                outliers = pd.DataFrame({"ep": [1.0], "is_lof_outlier": [False], "is_if_outlier": [False]})
                outliers[flag] = True

                self.assertEqual(create_errors({"ep": outliers}), [123])

                created = self.errors.bulk_create.call_args.args[0]
                self.assertEqual([(item.error, item.lot_id) for item in created], [(error, 123)])

    def test_returned_lot_ids_are_unique_across_models_and_emissions(self):
        outliers = pd.DataFrame({"ep": [1.0], "is_lof_outlier": [True], "is_if_outlier": [True]})

        lot_ids = create_errors({"ep": outliers, "eec": outliers.rename(columns={"ep": "eec"})})

        self.assertEqual(lot_ids, [123])
        self.assertEqual(len(self.errors.bulk_create.call_args.args[0]), 4)
