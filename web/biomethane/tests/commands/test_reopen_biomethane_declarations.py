from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from biomethane.models import BiomethaneAnnualDeclaration
from core.models import Entity, UserRights
from core.tests_utils import setup_current_user


class ReopenBiomethaneDeclarationsTests(TestCase):
    def setUp(self):
        self.producer = Entity.objects.create(
            name="Producteur test",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        self.year = 2025
        self.declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer,
            year=self.year,
            status=BiomethaneAnnualDeclaration.DECLARED,
            is_open=False,
        )
        setup_current_user(self, "admin@example.com", "Admin", "pass", [(self.producer, UserRights.ADMIN)])
        setup_current_user(self, "writer@example.com", "Writer", "pass", [(self.producer, UserRights.RW)])
        setup_current_user(self, "reader@example.com", "Reader", "pass", [(self.producer, UserRights.RO)])

    @patch("biomethane.management.commands.reopen_biomethane_declarations.send_mail")
    def test_reopens_declaration_and_emails_admin_and_writer(self, send_mail):
        call_command(
            "reopen_biomethane_declarations",
            year=self.year,
            entity_ids=str(self.producer.id),
            dry_run="false",
        )

        self.declaration.refresh_from_db()
        self.assertTrue(self.declaration.is_open)
        self.assertEqual(self.declaration.status, BiomethaneAnnualDeclaration.IN_PROGRESS)
        send_mail.assert_called_once()
        self.assertEqual(
            send_mail.call_args.kwargs["recipient_list"],
            ["admin@example.com", "writer@example.com"],
        )
        self.assertIn(str(self.year), send_mail.call_args.kwargs["subject"])
        self.assertIn(str(self.year), send_mail.call_args.kwargs["message"])

    @patch("biomethane.management.commands.reopen_biomethane_declarations.send_mail")
    def test_skips_entity_without_declaration(self, send_mail):
        call_command(
            "reopen_biomethane_declarations",
            year=self.year + 1,
            entity_ids=str(self.producer.id),
            dry_run="false",
        )

        self.declaration.refresh_from_db()
        self.assertFalse(self.declaration.is_open)
        self.assertEqual(self.declaration.status, BiomethaneAnnualDeclaration.DECLARED)
        send_mail.assert_not_called()
