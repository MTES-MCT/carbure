import json
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.management.commands import migrate_entity_ownership as command_module
from core.models import Department, Entity, UserPreferences, UserRights, UserRightsRequests
from entity.models import EntityScope

User = get_user_model()


def run_command(source, target, apply=False):
    return json.loads(
        call_command(
            "migrate_entity_ownership",
            source.name,
            target.name,
            apply=apply,
            stdout=StringIO(),
        )
    )


def get_field_report(report, model, field):
    for field_report in report["fields"]:
        if field_report["model"] == model and field_report["field"] == field:
            return field_report
    raise AssertionError(f"Missing field report for {model}.{field}")


class MigrateEntityOwnershipCommandTest(TestCase):
    def setUp(self):
        self.source = Entity.objects.create(name="Source entity", entity_type=Entity.OPERATOR)
        self.target = Entity.objects.create(name="Target entity", entity_type=Entity.OPERATOR, is_enabled=True)
        self.user = User.objects.create_user(email="user@example.com", name="User")

    def test_dry_run_reports_counts_without_mutating_records(self):
        UserPreferences.objects.create(user=self.user, default_entity=self.source)
        UserRights.objects.create(user=self.user, entity=self.source)
        UserRightsRequests.objects.create(user=self.user, entity=self.source)

        report = run_command(self.source, self.target)

        self.assertEqual(report["source_entity"], self.source.name)
        self.assertEqual(report["target_entity"], self.target.name)
        self.assertEqual(get_field_report(report, "core.UserPreferences", "default_entity")["source_count"], 1)
        self.assertEqual(get_field_report(report, "core.UserRights", "entity")["source_count"], 1)
        self.assertEqual(get_field_report(report, "core.UserRightsRequests", "entity")["source_count"], 1)
        self.assertEqual(get_field_report(report, "core.UserPreferences", "default_entity")["updated"], 0)

        self.assertEqual(UserPreferences.objects.get(user=self.user).default_entity_id, self.source.id)
        self.assertEqual(UserRights.objects.get(user=self.user).entity_id, self.source.id)
        self.assertEqual(UserRightsRequests.objects.get(user=self.user).entity_id, self.source.id)

    def test_apply_migrates_allowlisted_fields_atomically_and_leaves_source_unchanged(self):
        preferences = UserPreferences.objects.create(user=self.user, default_entity=self.source)
        rights_request = UserRightsRequests.objects.create(user=self.user, entity=self.source)
        department = Department.objects.create(code_dept="01", name="Ain")
        content_type = ContentType.objects.get_for_model(Department)
        scope = EntityScope.objects.create(entity=self.source, content_type=content_type, object_id=department.id)

        report = run_command(self.source, self.target, apply=True)

        preferences.refresh_from_db()
        rights_request.refresh_from_db()
        scope.refresh_from_db()
        self.source.refresh_from_db()

        self.assertEqual(get_field_report(report, "core.UserPreferences", "default_entity")["updated"], 1)
        self.assertEqual(get_field_report(report, "core.UserRightsRequests", "entity")["updated"], 1)
        self.assertEqual(get_field_report(report, "entity.EntityScope", "entity")["updated"], 1)
        self.assertEqual(preferences.default_entity_id, self.target.id)
        self.assertEqual(rights_request.entity_id, self.target.id)
        self.assertEqual(scope.entity_id, self.target.id)
        self.assertIsNone(self.source.closed_at)
        self.assertTrue(self.source.is_enabled)

    def test_same_source_and_target_fails(self):
        with self.assertRaises(CommandError):
            run_command(self.source, self.source)

    def test_config_validation_catches_missing_field(self):
        with patch.object(command_module, "MIGRATED_ENTITY_FIELDS", (("core", "Entity", "missing_field"),)):
            with self.assertRaises(CommandError):
                command_module.validate_migrated_entity_fields()

    def test_config_validation_catches_non_entity_field(self):
        with patch.object(command_module, "MIGRATED_ENTITY_FIELDS", (("core", "Entity", "name"),)):
            with self.assertRaises(CommandError):
                command_module.validate_migrated_entity_fields()
