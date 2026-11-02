from importlib import import_module

from django.apps import apps
from django.db import connection
from django.test import TestCase

from core.models import CarbureLot, GenericError


class LegacyMLErrorCleanupTest(TestCase):
    def test_removes_legacy_errors_and_preserves_current_checks(self):
        lot = CarbureLot.objects.create(year=2026, period=202601)
        legacy_errors = [
            "EEC_ANORMAL_LOW",
            "EEC_ANORMAL_HIGH",
            "EP_ANORMAL_LOW",
            "EP_ANORMAL_HIGH",
            "ETD_ANORMAL_HIGH",
            "ETD_NO_EU_TOO_LOW",
            "ETD_EU_DEFAULT_VALUE",
            "ETD_HIGHER_THAN_DEFAULT",
        ]
        current_errors = ["OUTLIER_EEC", "OUTLIER_EP", "OUTLIER_ETD", "GHG_ETD_0"]
        GenericError.objects.bulk_create([GenericError(lot=lot, error=error) for error in legacy_errors + current_errors])
        migration = import_module("core.migrations.0089_remove_legacy_ml_errors")

        with connection.schema_editor(atomic=False) as schema_editor:
            migration.delete_legacy_ml_errors(apps, schema_editor)

        self.assertCountEqual(GenericError.objects.filter(lot=lot).values_list("error", flat=True), current_errors)
