from decimal import Decimal

from django.test import TestCase

from traceability.factories import ActionFactory
from traceability.models import Action
from traceability.services.total_emissions import annotate_total_emissions, parent_chain


class TotalEmissionsTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.root = ActionFactory.create(
            industry=Action.H2,
            type=Action.INIT,
            parent=None,
            ei=Decimal("1.000"),
            ep=Decimal("2.000"),
            etd=Decimal("3.000"),
            eu=Decimal("4.000"),
            eccs=Decimal("5.000"),
        )
        self.middle = ActionFactory.create(
            industry=Action.H2,
            type=Action.VALORIZE,
            parent=self.root,
            ei=Decimal("10.000"),
            ep=Decimal("20.000"),
            etd=Decimal("30.000"),
            eu=Decimal("40.000"),
            eccs=Decimal("50.000"),
        )
        self.leaf = ActionFactory.create(
            industry=Action.H2,
            type=Action.VALORIZE,
            parent=self.middle,
            ei=Decimal("100.000"),
            ep=Decimal("200.000"),
            etd=Decimal("300.000"),
            eu=Decimal("400.000"),
            eccs=Decimal("500.000"),
        )

    def test_parent_chain_walks_up_to_the_root(self):
        chain = list(parent_chain(Action.objects.filter(pk=self.leaf.pk)))

        self.assertEqual(len(chain), 3)
        self.assertCountEqual(
            [row["ancestor_id"] for row in chain],
            [self.leaf.pk, self.middle.pk, self.root.pk],
        )

    def test_lowest_action_total_emissions_sums_the_parent_chain(self):
        annotated_actions = list(annotate_total_emissions(Action.objects.all()))

        self.assertEqual(
            annotated_actions[0].total_emissions,
            {
                "ei": Decimal("1.000"),
                "ep": Decimal("2.000"),
                "etd": Decimal("3.000"),
                "eu": Decimal("4.000"),
                "eccs": Decimal("5.000"),
                "total": Decimal("5.000"),
            },
        )

        self.assertEqual(
            annotated_actions[1].total_emissions,
            {
                "ei": Decimal("11.000"),
                "ep": Decimal("22.000"),
                "etd": Decimal("33.000"),
                "eu": Decimal("44.000"),
                "eccs": Decimal("55.000"),
                "total": Decimal("55.000"),
            },
        )

        self.assertEqual(
            annotated_actions[2].total_emissions,
            {
                "ei": Decimal("111.000"),
                "ep": Decimal("222.000"),
                "etd": Decimal("333.000"),
                "eu": Decimal("444.000"),
                "eccs": Decimal("555.000"),
                "total": Decimal("555.000"),
            },
        )
