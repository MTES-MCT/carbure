from django.test import SimpleTestCase

from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.h2 import H2ActionHandler
from traceability.models import Action
from traceability.services.action_excel import resolve_action_excel_columns


class ActionExcelTemplateTest(SimpleTestCase):
    def test_default_columns_keep_generic_labels(self):
        columns = resolve_action_excel_columns(ActionIndustryHandler())
        labels = {column.key: column.label for column in columns}

        self.assertEqual(labels["pos_id"], "N° de POS")
        self.assertEqual(labels["quantity"], "Quantité")
        self.assertEqual(
            next(column.options for column in columns if column.key == "shipping_method"),
            [label for _, label in Action.SHIPPING_METHODS],
        )

    def test_h2_handler_overrides_quantity_label(self):
        columns = resolve_action_excel_columns(H2ActionHandler())
        labels = {column.key: column.label for column in columns}

        self.assertEqual(labels["quantity"], "Quantité (MJ)")
        self.assertEqual(labels["pos_id"], "N° de POS")
