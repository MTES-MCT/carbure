from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from traceability.factories import ActionFactory, MaterialFactory
from traceability.models import Action
from traceability.services.inherited_fields import attach_inherited_fields
from traceability.services.parent_chain import annotate_parent_chain


class ParentChainTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        hydrogen = MaterialFactory(code="H2", name="Hydrogène")
        self.root = ActionFactory.create(industry=Action.H2, parent=None, material=hydrogen, ei=1)
        self.leaf = ActionFactory.create(industry=Action.H2, parent=self.root, material=None, ei=10)

    def _sql(self, **flags):
        with CaptureQueriesContext(connection) as captured:
            list(annotate_parent_chain(Action.objects.filter(pk=self.leaf.pk), **flags))
        return " ".join(query["sql"] for query in captured.captured_queries)

    def test_both_flags_are_one_statement(self):
        sql = self._sql()
        action = annotate_parent_chain(Action.objects.filter(pk=self.leaf.pk)).get()
        attach_inherited_fields([action])

        self.assertEqual(sql.lower().count("with recursive"), 1)
        self.assertIn("previous_material_id", sql)
        self.assertIn("origin_material_id", sql)
        self.assertIn("ei_sum", sql)
        self.assertEqual(action.inherited_fields["previous_material"].code, "H2")
        self.assertEqual(action.inherited_fields["origin_material"].code, "H2")
        self.assertEqual(action.total_emissions["ei"], Decimal("11.000"))

    def test_emissions_only_omits_the_material_column(self):
        sql = self._sql(inherited_fields=False)

        self.assertNotIn("previous_material_id", sql)
        self.assertNotIn("origin_material_id", sql)
        self.assertIn("ei_sum", sql)

    def test_neither_flag_leaves_the_queryset_unchanged(self):
        queryset = Action.objects.filter(pk=self.leaf.pk)

        self.assertIs(annotate_parent_chain(queryset, emissions=False, inherited_fields=False), queryset)
