import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Entity
from elec.factories import ElecProvisionCertificateQualichargeFactory


def run_command(apply=False):
    return json.loads(call_command("relink_qualicharge_unknown_siren", apply=apply, stdout=StringIO()))


class RelinkQualichargeUnknownSirenCommandTest(TestCase):
    def setUp(self):
        self.resolvable_siren = "111111111"
        self.unknown_siren = "999999999"
        self.multiple_without_master_siren = "222222222"
        self.disabled_cpo_siren = "333333333"
        self.operator_siren = "444444444"

        self.resolved_cpo = Entity.objects.create(
            name="Resolvable CPO",
            entity_type=Entity.CPO,
            registration_id=self.resolvable_siren,
            is_enabled=True,
        )

        Entity.objects.create(
            name="Duplicate CPO 1",
            entity_type=Entity.CPO,
            registration_id=self.multiple_without_master_siren,
            is_master=False,
            is_enabled=True,
        )
        Entity.objects.create(
            name="Duplicate CPO 2",
            entity_type=Entity.CPO,
            registration_id=self.multiple_without_master_siren,
            is_master=False,
            is_enabled=True,
        )

        Entity.objects.create(
            name="Disabled CPO",
            entity_type=Entity.CPO,
            registration_id=self.disabled_cpo_siren,
            is_enabled=False,
        )

        Entity.objects.create(
            name="Oil operator",
            entity_type=Entity.OPERATOR,
            registration_id=self.operator_siren,
            is_enabled=True,
        )

    def test_dry_run_reports_only_resolvable_certificates(self):
        cert_resolvable = ElecProvisionCertificateQualichargeFactory(cpo=None, unknown_siren=self.resolvable_siren)
        cert_unknown = ElecProvisionCertificateQualichargeFactory(cpo=None, unknown_siren=self.unknown_siren)
        cert_duplicates = ElecProvisionCertificateQualichargeFactory(
            cpo=None,
            unknown_siren=self.multiple_without_master_siren,
        )
        cert_disabled = ElecProvisionCertificateQualichargeFactory(cpo=None, unknown_siren=self.disabled_cpo_siren)
        cert_operator = ElecProvisionCertificateQualichargeFactory(cpo=None, unknown_siren=self.operator_siren)

        report = run_command(apply=False)

        cert_resolvable.refresh_from_db()
        self.assertIsNone(cert_resolvable.cpo)
        self.assertEqual(cert_resolvable.unknown_siren, self.resolvable_siren)

        self.assertTrue(report["dry_run"])
        self.assertEqual(report["total_problematic_certificates"], 5)
        self.assertEqual(report["total_problematic_sirens"], 5)
        self.assertEqual(report["resolvable_sirens"], 1)
        self.assertEqual(report["unresolved_sirens"], 4)
        self.assertEqual(report["resolvable_certificates"], 1)
        self.assertEqual(report["updated_certificates"], 0)

        unresolved = set(report["sample_unresolved_sirens"])
        self.assertIn(self.unknown_siren, unresolved)
        self.assertIn(self.multiple_without_master_siren, unresolved)
        self.assertIn(self.disabled_cpo_siren, unresolved)
        self.assertIn(self.operator_siren, unresolved)

        # Keep references used above to make intent explicit.
        self.assertIsNotNone(cert_unknown.id)
        self.assertIsNotNone(cert_duplicates.id)
        self.assertIsNotNone(cert_disabled.id)
        self.assertIsNotNone(cert_operator.id)

    def test_apply_updates_only_resolvable_unknown_sirens(self):
        first_resolvable = ElecProvisionCertificateQualichargeFactory(cpo=None, unknown_siren=self.resolvable_siren)
        second_resolvable = ElecProvisionCertificateQualichargeFactory(cpo=None, unknown_siren=self.resolvable_siren)
        non_resolvable = ElecProvisionCertificateQualichargeFactory(cpo=None, unknown_siren=self.unknown_siren)
        already_linked = ElecProvisionCertificateQualichargeFactory(
            cpo=self.resolved_cpo, unknown_siren=self.resolvable_siren
        )

        report = run_command(apply=True)

        first_resolvable.refresh_from_db()
        second_resolvable.refresh_from_db()
        non_resolvable.refresh_from_db()
        already_linked.refresh_from_db()

        self.assertFalse(report["dry_run"])
        self.assertEqual(report["total_problematic_certificates"], 3)
        self.assertEqual(report["resolvable_certificates"], 2)
        self.assertEqual(report["updated_certificates"], 2)
        self.assertEqual(report["updated_by_cpo"], {str(self.resolved_cpo.id): 2})

        self.assertEqual(first_resolvable.cpo_id, self.resolved_cpo.id)
        self.assertIsNone(first_resolvable.unknown_siren)
        self.assertEqual(second_resolvable.cpo_id, self.resolved_cpo.id)
        self.assertIsNone(second_resolvable.unknown_siren)

        self.assertIsNone(non_resolvable.cpo)
        self.assertEqual(non_resolvable.unknown_siren, self.unknown_siren)

        # Certificates already linked to a CPO are not part of the targeted queryset.
        self.assertEqual(already_linked.cpo_id, self.resolved_cpo.id)
        self.assertEqual(already_linked.unknown_siren, self.resolvable_siren)
