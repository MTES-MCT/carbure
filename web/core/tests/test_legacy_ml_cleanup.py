from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.migrations.state import ProjectState
from django.test import TestCase, TransactionTestCase

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


class LegacyMLAppCleanupTest(TransactionTestCase):
    tables = ["ml_eec_stats", "ml_ep_stats", "ml_etd_stats"]

    def apply_cleanup(self):
        migration_module = import_module("core.migrations.0091_remove_legacy_ml_app")
        migration = migration_module.Migration("0091_remove_legacy_ml_app", "core")
        with connection.schema_editor(atomic=False) as schema_editor:
            migration.apply(ProjectState.from_apps(apps), schema_editor)

    def test_removes_existing_tables_and_permissions(self):
        with connection.cursor() as cursor:
            for table in self.tables:
                cursor.execute(f"CREATE TABLE {connection.ops.quote_name(table)} (id INTEGER PRIMARY KEY)")
                cursor.execute(f"INSERT INTO {connection.ops.quote_name(table)} (id) VALUES (1)")
        for model in ["eecstats", "epstats", "etdstats"]:
            content_type = ContentType.objects.create(app_label="ml", model=model)
            Permission.objects.create(content_type=content_type, codename=f"view_{model}", name=f"View {model}")
        current_content_type = ContentType.objects.get_for_model(CarbureLot)

        self.apply_cleanup()

        self.assertTrue(set(self.tables).isdisjoint(connection.introspection.table_names()))
        self.assertFalse(ContentType.objects.filter(app_label="ml").exists())
        self.assertFalse(Permission.objects.filter(content_type__app_label="ml").exists())
        self.assertTrue(ContentType.objects.filter(pk=current_content_type.pk).exists())
        self.assertIn("carbure_lots", connection.introspection.table_names())

    def test_succeeds_without_legacy_tables_on_fresh_installs(self):
        self.assertTrue(set(self.tables).isdisjoint(connection.introspection.table_names()))

        self.apply_cleanup()

        self.assertIn("carbure_lots", connection.introspection.table_names())
