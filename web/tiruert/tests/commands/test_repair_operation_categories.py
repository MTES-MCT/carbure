from datetime import date
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models import Biocarburant, Entity, MatierePremiere
from tiruert.factories import OperationDetailFactory, OperationFactory
from tiruert.models import Operation, OperationDetail
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


class RepairOperationCategoriesCommandTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/countries.json",
        "json/entities.json",
        "json/depots.json",
        "json/feedstock.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.entity = Entity.objects.filter(entity_type=Entity.OPERATOR).first()
        cls.debited_entity = Entity.objects.exclude(id=cls.entity.id).first()
        cls.biofuel = Biocarburant.objects.filter(compatible_diesel=True).first()
        cls.depot = Depot.objects.first()
        cls.other_feedstock = MatierePremiere.objects.create(
            name="Autre matière première",
            name_en="Other feedstock",
            description="",
            code="TEST_OTHER_FEEDSTOCK",
            compatible_alcool=False,
            compatible_graisse=True,
            is_double_compte=False,
            is_huile_vegetale=False,
            is_displayed=True,
            category=MatierePremiere.OTHER,
            is_biofuel_feedstock=True,
        )
        cls.cat3_feedstock = MatierePremiere.objects.create(
            name="Huiles ou graisses animales (catégorie III)",
            name_en="CIII animal fat",
            description="",
            code="HUILES_OU_GRAISSES_ANIMALES_CAT3",
            compatible_alcool=False,
            compatible_graisse=True,
            is_double_compte=False,
            is_huile_vegetale=False,
            is_displayed=True,
            category=MatierePremiere.CAT3,
            is_biofuel_feedstock=True,
        )
        cls.ann_ix_a_feedstock = MatierePremiere.biofuel.filter(category=MatierePremiere.IXA).first()
        cls.ep2_feedstock = MatierePremiere.biofuel.get(code="EP2")

    def _call_command(self, apply=True):
        out = StringIO()
        call_command("repair_operation_categories", apply=apply, stdout=out)
        return out.getvalue()

    def _create_lot(self, feedstock, volume=1000):
        return CarbureLotFactory.create(
            feedstock=feedstock,
            biofuel=self.biofuel,
            volume=volume,
            carbure_client=self.entity,
            carbure_supplier=self.debited_entity,
            carbure_delivery_site=self.depot,
        )

    def _create_other_operation(self, **kwargs):
        defaults = {
            "type": Operation.CESSION,
            "status": Operation.DECLARED,
            "customs_category": MatierePremiere.OTHER,
            "biofuel": self.biofuel,
            "credited_entity": self.entity,
            "debited_entity": self.debited_entity,
            "from_depot": self.depot,
            "to_depot": self.depot,
            "export_country": None,
            "export_recipient": "Recipient",
            "validation_date": date(2026, 1, 12),
            "renewable_energy_share": 0.8,
            "durability_period": "202501",
            "objective_sector": Operation.GAZOLE,
            "declaration_year": 2026,
        }
        defaults.update(kwargs)
        return OperationFactory.create(**defaults)

    def test_splits_mixed_operation_by_moving_mismatched_details_to_category_operation(self):
        operation = self._create_other_operation()
        other_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.other_feedstock),
            volume=100,
            emission_rate_per_mj=12,
        )
        cat3_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.cat3_feedstock),
            volume=200,
            emission_rate_per_mj=18,
        )
        original_created_at = operation.created_at

        output = self._call_command()

        self.assertIn("Split 1 mismatched category group(s)", output)
        operation.refresh_from_db()
        self.assertEqual(operation.customs_category, MatierePremiere.OTHER)
        self.assertQuerySetEqual(
            operation.details.order_by("id"),
            [other_detail],
            transform=lambda detail: detail,
        )

        cat3_operation = Operation.objects.exclude(id=operation.id).get()
        self.assertEqual(cat3_operation.customs_category, MatierePremiere.CAT3)
        self.assertEqual(cat3_operation.type, operation.type)
        self.assertEqual(cat3_operation.status, operation.status)
        self.assertEqual(cat3_operation.biofuel, operation.biofuel)
        self.assertEqual(cat3_operation.credited_entity, operation.credited_entity)
        self.assertEqual(cat3_operation.debited_entity, operation.debited_entity)
        self.assertEqual(cat3_operation.from_depot, operation.from_depot)
        self.assertEqual(cat3_operation.to_depot, operation.to_depot)
        self.assertEqual(cat3_operation.export_country, operation.export_country)
        self.assertEqual(cat3_operation.export_recipient, operation.export_recipient)
        self.assertEqual(cat3_operation.validation_date, operation.validation_date)
        self.assertEqual(cat3_operation.renewable_energy_share, operation.renewable_energy_share)
        self.assertEqual(cat3_operation.durability_period, operation.durability_period)
        self.assertEqual(cat3_operation.objective_sector, operation.objective_sector)
        self.assertEqual(cat3_operation.declaration_year, operation.declaration_year)
        self.assertEqual(cat3_operation.created_at, original_created_at)
        cat3_detail.refresh_from_db()
        self.assertEqual(cat3_detail.operation, cat3_operation)

    def test_reports_impacted_operations_without_apply(self):
        operation = self._create_other_operation()
        OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.cat3_feedstock),
            volume=200,
            emission_rate_per_mj=18,
        )

        output = self._call_command(apply=False)

        operation.refresh_from_db()
        self.assertIn("Dry run. Use --apply to repair data", output)
        self.assertEqual(Operation.objects.count(), 1)
        self.assertEqual(operation.customs_category, MatierePremiere.OTHER)

    def test_splits_any_feedstock_category_mismatch_not_only_cat3(self):
        operation = self._create_other_operation()
        ix_a_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.ann_ix_a_feedstock),
            volume=200,
            emission_rate_per_mj=18,
        )

        output = self._call_command()

        self.assertIn("Updated 1 operation(s) in place", output)
        operation.refresh_from_db()
        ix_a_detail.refresh_from_db()
        self.assertEqual(Operation.objects.count(), 1)
        self.assertEqual(operation.customs_category, MatierePremiere.IXA)
        self.assertEqual(ix_a_detail.operation, operation)

    def test_splits_one_operation_into_multiple_mismatched_category_groups(self):
        operation = self._create_other_operation()
        other_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.other_feedstock),
            volume=100,
            emission_rate_per_mj=12,
        )
        cat3_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.cat3_feedstock),
            volume=200,
            emission_rate_per_mj=18,
        )
        ix_a_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.ann_ix_a_feedstock),
            volume=300,
            emission_rate_per_mj=20,
        )

        output = self._call_command()

        self.assertIn("Split 2 mismatched category group(s)", output)
        operation.refresh_from_db()
        self.assertQuerySetEqual(
            operation.details.order_by("id"),
            [other_detail],
            transform=lambda detail: detail,
        )
        cat3_detail.refresh_from_db()
        ix_a_detail.refresh_from_db()
        self.assertEqual(cat3_detail.operation.customs_category, MatierePremiere.CAT3)
        self.assertEqual(ix_a_detail.operation.customs_category, MatierePremiere.IXA)
        self.assertEqual(Operation.objects.count(), 3)

    def test_deletes_original_operation_when_no_details_match_its_category_after_split(self):
        operation = self._create_other_operation()
        cat3_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.cat3_feedstock),
            volume=200,
            emission_rate_per_mj=18,
        )
        ix_a_detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.ann_ix_a_feedstock),
            volume=300,
            emission_rate_per_mj=20,
        )

        output = self._call_command()

        self.assertIn("Split 2 mismatched category group(s)", output)
        self.assertFalse(Operation.objects.filter(id=operation.id).exists())
        cat3_detail.refresh_from_db()
        ix_a_detail.refresh_from_db()
        self.assertEqual(cat3_detail.operation.customs_category, MatierePremiere.CAT3)
        self.assertEqual(ix_a_detail.operation.customs_category, MatierePremiere.IXA)
        self.assertEqual(Operation.objects.count(), 2)

    def test_updates_all_mismatched_operation_in_place_without_creating_empty_original(self):
        operation = self._create_other_operation()
        detail = OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.cat3_feedstock),
            volume=200,
            emission_rate_per_mj=18,
        )

        output = self._call_command()

        self.assertIn("Updated 1 operation(s) in place", output)
        operation.refresh_from_db()
        detail.refresh_from_db()
        self.assertEqual(Operation.objects.count(), 1)
        self.assertEqual(operation.customs_category, MatierePremiere.CAT3)
        self.assertEqual(detail.operation, operation)

    def test_leaves_operations_without_category_mismatch_untouched(self):
        operation = self._create_other_operation()
        OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.other_feedstock),
            volume=100,
            emission_rate_per_mj=12,
        )

        output = self._call_command()

        operation.refresh_from_db()
        self.assertIn("No operations with feedstock category mismatches found", output)
        self.assertEqual(Operation.objects.count(), 1)
        self.assertEqual(operation.customs_category, MatierePremiere.OTHER)

    def test_leaves_ep2_operations_split_to_conv_or_ep2am_untouched(self):
        conv_operation = self._create_other_operation(customs_category=MatierePremiere.CONV)
        ep2am_operation = self._create_other_operation(customs_category=MatierePremiere.EP2AM)
        OperationDetailFactory.create_for_operation(
            conv_operation,
            lot=self._create_lot(self.ep2_feedstock),
            volume=40,
            emission_rate_per_mj=12,
        )
        OperationDetailFactory.create_for_operation(
            ep2am_operation,
            lot=self._create_lot(self.ep2_feedstock),
            volume=60,
            emission_rate_per_mj=12,
        )

        output = self._call_command()

        conv_operation.refresh_from_db()
        ep2am_operation.refresh_from_db()
        self.assertIn("No operations with feedstock category mismatches found", output)
        self.assertEqual(Operation.objects.count(), 2)
        self.assertEqual(conv_operation.customs_category, MatierePremiere.CONV)
        self.assertEqual(ep2am_operation.customs_category, MatierePremiere.EP2AM)

    def test_command_is_idempotent_after_splitting(self):
        operation = self._create_other_operation()
        OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.other_feedstock),
            volume=100,
            emission_rate_per_mj=12,
        )
        OperationDetailFactory.create_for_operation(
            operation,
            lot=self._create_lot(self.cat3_feedstock),
            volume=200,
            emission_rate_per_mj=18,
        )

        self._call_command()
        output = self._call_command()

        self.assertIn("No operations with feedstock category mismatches found", output)
        self.assertEqual(Operation.objects.count(), 2)
        self.assertEqual(Operation.objects.filter(customs_category=MatierePremiere.OTHER).count(), 1)
        self.assertEqual(Operation.objects.filter(customs_category=MatierePremiere.CAT3).count(), 1)
        self.assertEqual(OperationDetail.objects.count(), 2)
