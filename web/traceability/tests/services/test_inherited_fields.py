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

    def test_previous_is_the_nearest_above_and_origin_is_the_root(self):
        by_id = self._by_id()

        self.assertIsNone(by_id[self.root.pk]["previous_material"])
        self.assertEqual(by_id[self.root.pk]["origin_material"].code, "H2")
        self.assertEqual(by_id[self.middle.pk]["previous_material"].code, "H2")
        self.assertEqual(by_id[self.middle.pk]["origin_material"].code, "H2")
        self.assertEqual(by_id[self.leaf.pk]["previous_material"].code, "H2")
        self.assertEqual(by_id[self.leaf.pk]["previous_material"].name, "Hydrogène")
        self.assertEqual(by_id[self.leaf.pk]["origin_material"].code, "H2")

    def test_a_closer_declaration_is_previous_and_the_root_stays_origin(self):
        self.middle.material = self.other
        self.middle.save(update_fields=["material"])

        by_id = self._by_id()

        self.assertIsNone(by_id[self.root.pk]["previous_material"])
        self.assertEqual(by_id[self.root.pk]["origin_material"].code, "H2")
        self.assertEqual(by_id[self.middle.pk]["previous_material"].code, "H2")
        self.assertEqual(by_id[self.middle.pk]["origin_material"].code, "H2")
        self.assertEqual(by_id[self.leaf.pk]["previous_material"].code, "CH4")
        self.assertEqual(by_id[self.leaf.pk]["origin_material"].code, "H2")

    def test_own_material_does_not_replace_previous_or_origin(self):
        self.leaf.material = self.other
        self.leaf.save(update_fields=["material"])

        leaf = self._by_id()[self.leaf.pk]

        self.assertEqual(leaf["previous_material"].code, "H2")
        self.assertEqual(leaf["origin_material"].code, "H2")

    def test_origin_is_the_action_when_nothing_above_declares_a_material(self):
        root = ActionFactory.create(industry=Action.H2, parent=None, material=None)
        child = ActionFactory.create(industry=Action.H2, parent=root, material=self.other)

        by_id = self._by_id()

        self.assertIsNone(by_id[root.pk]["previous_material"])
        self.assertIsNone(by_id[root.pk]["origin_material"])
        self.assertIsNone(by_id[child.pk]["previous_material"])
        self.assertEqual(by_id[child.pk]["origin_material"].code, "CH4")
