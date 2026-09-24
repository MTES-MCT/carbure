from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import serializers

from core.excel_importer import ExcelValidationError
from tiruert.models import Operation
from tiruert.services.operation_excel_import import OperationExcelImportService, OperationGroup, _default_status


class OperationExcelImportServiceHelpersTest(TestCase):
    def _make_biofuel(self, biofuel_id=1, code="ETH", pci_litre=10, renewable_energy_share=1):
        return SimpleNamespace(
            id=biofuel_id,
            code=code,
            pci_litre=pci_litre,
            renewable_energy_share=renewable_energy_share,
            compatible_essence=True,
            compatible_diesel=False,
        )

    def _make_lot(self, lot_id=1, category="CONV", biofuel=None):
        if biofuel is None:
            biofuel = self._make_biofuel()
        return SimpleNamespace(
            id=lot_id,
            feedstock=SimpleNamespace(category=category),
            biofuel=biofuel,
            biofuel_id=biofuel.id,
        )

    def _make_group(
        self,
        operation_type=Operation.TENEUR,
        customs_category="CONV",
        biofuel=None,
        credited_entity=None,
        debited_entity=None,
        lot_volumes=None,
        rows=None,
    ):
        if biofuel is None:
            biofuel = self._make_biofuel()
        if debited_entity is None:
            debited_entity = SimpleNamespace(id=10, name="Debited")
        if lot_volumes is None:
            lot_volumes = {1: 100.0}
        if rows is None:
            rows = [3]

        return OperationGroup(
            operation_type=operation_type,
            customs_category=customs_category,
            biofuel_id=biofuel.id,
            biofuel_code=biofuel.code,
            biofuel=biofuel,
            sector=Operation.ESSENCE,
            credited_entity=credited_entity,
            debited_entity=debited_entity,
            row_numbers=rows,
            lot_volumes=lot_volumes,
        )

    @patch("tiruert.services.operation_excel_import.ExcelImporter.parse")
    def test_parse_rows_filters_empty_volume_and_drops_display_columns(self, mock_parse):
        """Should keep only rows with a volume and strip display-only columns before validation."""
        mock_parse.return_value = [
            {
                "lot_id": 1,
                "volume": 100,
                "carbure_id": "CARB-1",
                "feedstock": "X",
                "biofuel": "ETH",
                "customs_category": "CONV",
                "available_volume": 200,
                "emission_rate_per_mj": 9.8,
                "credited_entity_name": "A",
                "operation_type": "TENEUR",
            },
            {"lot_id": 2, "volume": None, "operation_type": "TENEUR"},
            {"lot_id": 3, "volume": "", "operation_type": "TRANSFERT"},
        ]

        rows = OperationExcelImportService._parse_rows(Mock())

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["lot_id"], 1)
        self.assertEqual(rows[0]["operation_type"], "TENEUR")
        self.assertNotIn("carbure_id", rows[0])
        self.assertNotIn("feedstock", rows[0])
        self.assertNotIn("credited_entity_name", rows[0])

    def test_extract_ids_keeps_unique_valid_integers(self):
        """Should return a deduplicated set of valid integer ids and ignore invalid values."""
        rows = [
            {"lot_id": "1"},
            {"lot_id": 2},
            {"lot_id": "2"},
            {"lot_id": None},
            {"lot_id": ""},
            {"lot_id": "bad"},
        ]

        ids = OperationExcelImportService._extract_ids(rows, "lot_id")

        self.assertEqual(ids, {1, 2})

    def test_build_groups_aggregates_same_lot_and_sets_excel_row_numbers(self):
        """Should aggregate duplicate lot lines in one group and keep original Excel row numbers."""
        biofuel = self._make_biofuel(1, "ETH")
        lot = self._make_lot(10, "CONV", biofuel)
        credited = SimpleNamespace(id=5, name="Credited")
        debited = SimpleNamespace(id=7, name="Debited")

        validated_rows = [
            {"operation_type": Operation.TRANSFERT, "lot_id": lot, "credited_entity": credited, "volume": 40.0},
            {"operation_type": Operation.TRANSFERT, "lot_id": lot, "credited_entity": credited, "volume": 60.0},
        ]

        groups = OperationExcelImportService._build_groups(validated_rows, debited)

        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group.row_numbers, [3, 4])
        self.assertEqual(group.lot_volumes, {10: 100.0})

    @patch("tiruert.services.operation_excel_import.OperationService.bulk_check_volumes")
    def test_validate_shared_lot_volumes_calls_bulk_check_for_multi_groups_only(self, mock_bulk_check_volumes):
        """Should run shared-volume validation only when at least two groups share the same biofuel/category."""
        debited = SimpleNamespace(id=1, name="Debited")
        same_biofuel = self._make_biofuel(1, "ETH")
        other_biofuel = self._make_biofuel(2, "EMAG")

        groups = [
            self._make_group(Operation.TENEUR, "CONV", same_biofuel, debited_entity=debited, lot_volumes={1: 10.0}),
            self._make_group(Operation.TRANSFERT, "CONV", same_biofuel, debited_entity=debited, lot_volumes={1: 5.0}),
            self._make_group(Operation.TENEUR, "ANN-IX-A", other_biofuel, debited_entity=debited, lot_volumes={2: 5.0}),
        ]

        messages = OperationExcelImportService._validate_shared_lot_volumes(groups)

        self.assertEqual(messages, [])
        mock_bulk_check_volumes.assert_called_once()
        entries, unit = mock_bulk_check_volumes.call_args.args
        self.assertEqual(unit, "l")
        self.assertEqual(len(entries), 2)

    @patch("tiruert.services.operation_excel_import.OperationService.bulk_check_volumes")
    def test_validate_shared_lot_volumes_does_not_call_bulk_check_without_shared_combo(self, mock_bulk_check_volumes):
        """Should not run shared-volume validation when each biofuel/category combo has a single group."""
        debited = SimpleNamespace(id=1, name="Debited")
        biofuel_eth = self._make_biofuel(1, "ETH")
        biofuel_emag = self._make_biofuel(2, "EMAG")

        groups = [
            self._make_group(Operation.TENEUR, "CONV", biofuel_eth, debited_entity=debited, lot_volumes={1: 10.0}),
            self._make_group(Operation.TRANSFERT, "ANN-IX-A", biofuel_eth, debited_entity=debited, lot_volumes={2: 5.0}),
            self._make_group(Operation.TENEUR, "CONV", biofuel_emag, debited_entity=debited, lot_volumes={3: 5.0}),
        ]

        messages = OperationExcelImportService._validate_shared_lot_volumes(groups)

        self.assertEqual(messages, [])
        mock_bulk_check_volumes.assert_not_called()

    @patch("tiruert.services.operation_excel_import.OperationService.bulk_check_volumes")
    def test_validate_shared_lot_volumes_flattens_validation_errors(self, mock_bulk_check_volumes):
        """Should flatten DRF validation errors from shared-volume checks into plain message strings."""
        debited = SimpleNamespace(id=1, name="Debited")
        biofuel = self._make_biofuel(1, "ETH")
        groups = [
            self._make_group(Operation.TENEUR, "CONV", biofuel, debited_entity=debited, lot_volumes={1: 10.0}),
            self._make_group(Operation.TRANSFERT, "CONV", biofuel, debited_entity=debited, lot_volumes={1: 5.0}),
        ]
        mock_bulk_check_volumes.side_effect = serializers.ValidationError({"volume": ["too much"]})

        messages = OperationExcelImportService._validate_shared_lot_volumes(groups)

        self.assertEqual(messages, ["too much"])

    @patch("tiruert.services.operation_excel_import.OperationService.bulk_check_objectives_compliance")
    def test_validate_teneur_objectives_aggregates_by_category(self, mock_bulk_check_objectives):
        """Should aggregate TENEUR objective checks by customs category across groups."""
        debited = SimpleNamespace(id=1, name="Debited")
        biofuel_eth = self._make_biofuel(1, "ETH", 10)
        biofuel_emag = self._make_biofuel(2, "EMAG", 20)

        groups = [
            self._make_group(Operation.TENEUR, "CONV", biofuel_eth, debited_entity=debited, lot_volumes={1: 10.0}),
            self._make_group(Operation.TENEUR, "CONV", biofuel_emag, debited_entity=debited, lot_volumes={2: 5.0}),
            self._make_group(Operation.TRANSFERT, "CONV", biofuel_eth, debited_entity=debited, lot_volumes={3: 5.0}),
        ]

        messages = OperationExcelImportService._validate_teneur_objectives(groups, 2026)

        self.assertEqual(messages, [])
        mock_bulk_check_objectives.assert_called_once()
        request, entity_id, entries, declaration_year = mock_bulk_check_objectives.call_args.args
        self.assertEqual(request.entity, debited)
        self.assertEqual(entity_id, 1)
        self.assertEqual(declaration_year, 2026)
        self.assertEqual(len(entries), 2)

    @patch("tiruert.services.operation_excel_import.OperationService.bulk_check_objectives_compliance")
    def test_validate_teneur_objectives_does_not_call_bulk_for_single_group(self, mock_bulk_check_objectives):
        """Should skip bulk objective validation when a category has only one TENEUR group."""
        debited = SimpleNamespace(id=1, name="Debited")
        biofuel_eth = self._make_biofuel(1, "ETH", 10)

        groups = [
            self._make_group(Operation.TENEUR, "CONV", biofuel_eth, debited_entity=debited, lot_volumes={1: 10.0}),
            self._make_group(Operation.TRANSFERT, "CONV", biofuel_eth, debited_entity=debited, lot_volumes={2: 5.0}),
        ]

        messages = OperationExcelImportService._validate_teneur_objectives(groups, 2026)

        self.assertEqual(messages, [])
        mock_bulk_check_objectives.assert_not_called()

    @patch("tiruert.services.operation_excel_import.OperationService.bulk_check_objectives_compliance")
    def test_validate_teneur_objectives_flattens_validation_errors(self, mock_bulk_check_objectives):
        """Should flatten DRF validation errors returned by bulk objective validation."""
        debited = SimpleNamespace(id=1, name="Debited")
        biofuel_eth = self._make_biofuel(1, "ETH", 10)
        biofuel_emag = self._make_biofuel(2, "EMAG", 20)

        groups = [
            self._make_group(Operation.TENEUR, "CONV", biofuel_eth, debited_entity=debited, lot_volumes={1: 10.0}),
            self._make_group(Operation.TENEUR, "CONV", biofuel_emag, debited_entity=debited, lot_volumes={2: 5.0}),
        ]
        mock_bulk_check_objectives.side_effect = serializers.ValidationError({"teneur": ["objective exceeded"]})

        messages = OperationExcelImportService._validate_teneur_objectives(groups, 2026)

        self.assertEqual(messages, ["objective exceeded"])

    @patch("tiruert.services.operation_excel_import.OperationService.perform_checks_before_create")
    def test_validate_group_calls_service_with_expected_arguments(self, mock_perform_checks):
        """Should pass normalized payload and request context to perform_checks_before_create."""
        debited = SimpleNamespace(id=42, name="Debited")
        biofuel = self._make_biofuel(1, "ETH", 10, renewable_energy_share=0.5)
        group = self._make_group(
            operation_type=Operation.TRANSFERT,
            customs_category="CONV",
            biofuel=biofuel,
            debited_entity=debited,
            lot_volumes={10: 40.0, 11: 60.0},
        )

        messages = OperationExcelImportService._validate_group(group, biofuel, 2026)

        self.assertEqual(messages, [])
        mock_perform_checks.assert_called_once()
        call_kwargs = mock_perform_checks.call_args.kwargs

        self.assertEqual(call_kwargs["entity_id"], 42)
        self.assertEqual(call_kwargs["declaration_year"], 2026)
        self.assertEqual(call_kwargs["data"]["type"], Operation.TRANSFERT)
        self.assertEqual(call_kwargs["data"]["customs_category"], "CONV")
        self.assertEqual(call_kwargs["data"]["biofuel"], biofuel)
        self.assertEqual(call_kwargs["data"]["renewable_energy_share"], 0.5)
        self.assertEqual(call_kwargs["data"]["debited_entity"], debited)
        self.assertEqual(call_kwargs["request"].entity, debited)
        self.assertEqual(call_kwargs["request"].GET, {})
        self.assertEqual(
            sorted(call_kwargs["selected_lots"], key=lambda x: x["id"]),
            [{"id": 10, "volume": 40.0}, {"id": 11, "volume": 60.0}],
        )

    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._validate_teneur_objectives")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._validate_shared_lot_volumes")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._validate_group")
    def test_validate_groups_raises_excel_validation_error_when_any_message(
        self, mock_validate_group, mock_validate_shared_lot, mock_validate_teneur
    ):
        """Should raise ExcelValidationError when any group-level or aggregate validation returns messages."""
        group = self._make_group(lot_volumes={1: 10.0})
        mock_validate_group.return_value = ["e1"]
        mock_validate_shared_lot.return_value = ["e2"]
        mock_validate_teneur.return_value = []

        with self.assertRaises(ExcelValidationError) as context:
            OperationExcelImportService._validate_groups([group], total_rows=4, declaration_year=2026)

        self.assertEqual(context.exception.total_rows_processed, 4)
        self.assertEqual(
            context.exception.validation_errors,
            [
                {"errors": {"validation": ["e1"]}},
                {"errors": {"validation": ["e2"]}},
            ],
        )

    def test_group_to_dict_uses_existing_operation_data(self):
        """Should serialize a group using existing operation metadata when an operation instance is provided."""
        debited = SimpleNamespace(id=1, name="Debited")
        credited = SimpleNamespace(id=2, name="Credited")
        group = self._make_group(
            operation_type=Operation.TRANSFERT,
            credited_entity=credited,
            debited_entity=debited,
            lot_volumes={1: 10.0, 2: 5.0},
            rows=[3, 4],
        )
        operation = SimpleNamespace(id=88, status=Operation.DRAFT)

        payload = OperationExcelImportService._group_to_dict(group, operation)

        self.assertEqual(payload["operation_id"], 88)
        self.assertEqual(payload["status"], Operation.DRAFT)
        self.assertEqual(payload["lot_count"], 2)
        self.assertEqual(payload["total_volume"], 15.0)

    def test_default_status_returns_expected_value_by_operation_type(self):
        """Should return PENDING for TENEUR and DRAFT for TRANSFERT or unknown operation types."""
        self.assertEqual(_default_status(Operation.TENEUR), Operation.PENDING)
        self.assertEqual(_default_status(Operation.TRANSFERT), Operation.DRAFT)
        self.assertEqual(_default_status("UNKNOWN"), Operation.DRAFT)


class OperationExcelImportServiceExecuteTest(TestCase):
    @patch("tiruert.services.operation_excel_import.OperationImportResponseSerializer")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._build_groups_data")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._create_operations")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._validate_groups")
    @patch("tiruert.services.operation_excel_import.DeclarationPeriodService.get_current_declaration_year")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._build_groups")
    @patch("tiruert.services.operation_excel_import.ExcelImporter.validate_retrieved_data")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._build_lookup_caches")
    @patch("tiruert.services.operation_excel_import.OperationExcelRowSerializer")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._parse_rows")
    def test_execute_validate_mode_does_not_create_operations(
        self,
        mock_parse_rows,
        mock_row_serializer_cls,
        mock_build_lookup_caches,
        mock_validate_retrieved_data,
        mock_build_groups,
        mock_get_current_declaration_year,
        mock_validate_groups,
        mock_create_operations,
        mock_build_groups_data,
        mock_response_serializer,
    ):
        """Should validate rows and build response in validate mode without creating operations."""
        debited = SimpleNamespace(id=1, name="Debited")
        parsed_rows = [{"lot_id": 1, "volume": 100, "operation_type": Operation.TENEUR}]
        mock_parse_rows.return_value = parsed_rows

        mock_row_serializer = Mock()
        mock_row_serializer.validated_data = [{"ok": True}]
        mock_row_serializer_cls.return_value = mock_row_serializer
        mock_build_lookup_caches.return_value = {"lot_cache": {}, "credited_entity_cache": {}}
        mock_validate_retrieved_data.return_value = mock_row_serializer
        mock_build_groups.return_value = [Mock()]
        mock_get_current_declaration_year.return_value = 2026
        mock_build_groups_data.return_value = [{"x": 1}]
        mock_response_serializer.side_effect = lambda payload: SimpleNamespace(data=payload)

        result = OperationExcelImportService.execute(Mock(), "validate", debited)

        mock_create_operations.assert_not_called()
        mock_validate_groups.assert_called_once_with(mock_build_groups.return_value, 1, 2026)
        self.assertEqual(result, {"mode": "validate", "operations": [{"x": 1}]})

    @patch("tiruert.services.operation_excel_import.OperationImportResponseSerializer")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._build_groups_data")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._create_operations")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._validate_groups")
    @patch("tiruert.services.operation_excel_import.DeclarationPeriodService.get_current_declaration_year")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._build_groups")
    @patch("tiruert.services.operation_excel_import.ExcelImporter.validate_retrieved_data")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._build_lookup_caches")
    @patch("tiruert.services.operation_excel_import.OperationExcelRowSerializer")
    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._parse_rows")
    def test_execute_create_mode_creates_operations(
        self,
        mock_parse_rows,
        mock_row_serializer_cls,
        mock_build_lookup_caches,
        mock_validate_retrieved_data,
        mock_build_groups,
        mock_get_current_declaration_year,
        mock_validate_groups,
        mock_create_operations,
        mock_build_groups_data,
        mock_response_serializer,
    ):
        """Should create operations and include created operation data in create mode response."""
        debited = SimpleNamespace(id=1, name="Debited")
        parsed_rows = [{"lot_id": 1, "volume": 100, "operation_type": Operation.TENEUR}]
        mock_parse_rows.return_value = parsed_rows

        mock_row_serializer = Mock()
        mock_row_serializer.validated_data = [{"ok": True}]
        mock_row_serializer_cls.return_value = mock_row_serializer
        mock_build_lookup_caches.return_value = {"lot_cache": {}, "credited_entity_cache": {}}
        mock_validate_retrieved_data.return_value = mock_row_serializer
        groups = [Mock()]
        mock_build_groups.return_value = groups
        mock_get_current_declaration_year.return_value = 2026
        operations = [Mock()]
        mock_create_operations.return_value = operations
        mock_build_groups_data.return_value = [{"created": True}]
        mock_response_serializer.side_effect = lambda payload: SimpleNamespace(data=payload)

        result = OperationExcelImportService.execute(Mock(), "create", debited)

        mock_create_operations.assert_called_once_with(groups, 2026)
        mock_build_groups_data.assert_called_once_with(groups, operations)
        self.assertEqual(result, {"mode": "create", "operations": [{"created": True}]})


class OperationExcelImportServiceCreateOperationsTest(TestCase):
    @patch("tiruert.services.operation_excel_import.OperationService.create_operation_with_details")
    @patch("tiruert.services.operation_excel_import.OperationService.build_details_data")
    def test_create_operation_for_group_passes_renewable_share_to_operation_payload(
        self, mock_build_details_data, mock_create_operation_with_details
    ):
        """Should propagate biofuel renewable_energy_share into operation creation payload."""
        debited = SimpleNamespace(id=1, name="Debited")
        credited = SimpleNamespace(id=2, name="Credited")
        biofuel = SimpleNamespace(
            id=1,
            code="ETH",
            pci_litre=10,
            renewable_energy_share=0.63,
            compatible_essence=True,
            compatible_diesel=False,
        )
        group = OperationGroup(
            operation_type=Operation.TRANSFERT,
            customs_category="CONV",
            biofuel_id=1,
            biofuel_code="ETH",
            biofuel=biofuel,
            sector=Operation.ESSENCE,
            credited_entity=credited,
            debited_entity=debited,
            row_numbers=[3],
            lot_volumes={10: 20.0},
        )

        mock_build_details_data.return_value = [{"lot_id": 10, "volume": 20.0}]
        mock_created_operation = Mock(id=101)
        mock_create_operation_with_details.return_value = mock_created_operation

        result = OperationExcelImportService._create_operation_for_group(
            group,
            declaration_year=2026,
            emissions_by_lot={10: 1.1},
        )

        self.assertEqual(result, mock_created_operation)
        mock_build_details_data.assert_called_once_with({10: 20.0}, {10: 1.1})
        mock_create_operation_with_details.assert_called_once()
        operation_data, details_data = mock_create_operation_with_details.call_args.args
        self.assertEqual(operation_data["renewable_energy_share"], 0.63)
        self.assertEqual(details_data, [{"lot_id": 10, "volume": 20.0}])

    @patch("tiruert.services.operation_excel_import.OperationExcelImportService._create_operation_for_group")
    @patch("tiruert.services.operation_excel_import.OperationService.get_emission_rates_by_lot")
    def test_create_operations_aggregates_all_lot_ids_for_emissions_lookup(
        self, mock_get_emission_rates_by_lot, mock_create_operation_for_group
    ):
        """Should fetch emission rates once with all lot ids collected across groups."""
        debited = SimpleNamespace(id=1, name="Debited")
        biofuel = SimpleNamespace(
            id=1,
            code="ETH",
            pci_litre=10,
            compatible_essence=True,
            compatible_diesel=False,
        )

        group_one = OperationGroup(
            operation_type=Operation.TENEUR,
            customs_category="CONV",
            biofuel_id=1,
            biofuel_code="ETH",
            biofuel=biofuel,
            sector=Operation.ESSENCE,
            credited_entity=None,
            debited_entity=debited,
            row_numbers=[3],
            lot_volumes={10: 20.0, 11: 30.0},
        )
        group_two = OperationGroup(
            operation_type=Operation.TRANSFERT,
            customs_category="CONV",
            biofuel_id=1,
            biofuel_code="ETH",
            biofuel=biofuel,
            sector=Operation.ESSENCE,
            credited_entity=SimpleNamespace(id=2, name="Credited"),
            debited_entity=debited,
            row_numbers=[4],
            lot_volumes={12: 15.0},
        )

        mock_get_emission_rates_by_lot.return_value = {10: 1.1, 11: 2.2, 12: 3.3}
        mock_create_operation_for_group.side_effect = [Mock(id=101), Mock(id=102)]

        operations = OperationExcelImportService._create_operations([group_one, group_two], 2026)

        mock_get_emission_rates_by_lot.assert_called_once_with([10, 11, 12])
        self.assertEqual(mock_create_operation_for_group.call_count, 2)
        self.assertEqual(len(operations), 2)
