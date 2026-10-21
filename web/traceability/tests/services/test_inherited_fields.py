from django.test import TestCase

from traceability.factories import ActionFactory, MaterialFactory
from traceability.models import Action
from traceability.services.inherited_fields import annotate_inherited_fields, attach_inherited_fields


class InheritedFieldsTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.hydrogen = MaterialFactory(code="H2", name="Hydrogène")
        self.other = MaterialFactory(code="CH4", name="Méthane")
        self.root = ActionFactory.create(industry=Action.H2, parent=None, material=self.hydrogen)
        self.middle = ActionFactory.create(industry=Action.H2, parent=self.root, material=None)
        self.leaf = ActionFactory.create(industry=Action.H2, parent=self.middle, material=None)

    def _by_id(self):
        actions = list(annotate_inherited_fields(Action.objects.all()))
        attach_inherited_fields(actions)
        return {action.pk: action.inherited_fields for action in actions}

    def test_material_comes_from_the_nearest_ancestor_that_declared_one(self):
        by_id = self._by_id()

        self.assertEqual(by_id[self.root.pk]["material"].code, "H2")
        self.assertEqual(by_id[self.middle.pk]["material"].code, "H2")
        self.assertEqual(by_id[self.leaf.pk]["material"].code, "H2")
        self.assertEqual(by_id[self.leaf.pk]["material"].name, "Hydrogène")

    def test_a_closer_declaration_wins_over_the_root(self):
        self.middle.material = self.other
        self.middle.save(update_fields=["material"])

        by_id = self._by_id()

        self.assertEqual(by_id[self.root.pk]["material"].code, "H2")
        self.assertEqual(by_id[self.middle.pk]["material"].code, "CH4")
        self.assertEqual(by_id[self.leaf.pk]["material"].code, "CH4")

    def test_missing_material_on_the_whole_chain_stays_null_and_keeps_the_action(self):
        empty = ActionFactory.create(industry=Action.H2, parent=None, material=None)
        wanted = [self.root.pk, self.middle.pk, self.leaf.pk, empty.pk]

        annotated = list(annotate_inherited_fields(Action.objects.filter(pk__in=wanted)))
        attach_inherited_fields(annotated)
        by_id = {action.pk: action.inherited_fields for action in annotated}

        self.assertCountEqual([action.pk for action in annotated], wanted)
        self.assertIsNone(by_id[empty.pk]["material"])
