from decimal import Decimal

from django.test import TestCase

from traceability.factories import ActionFactory
from traceability.models import Action
from traceability.services.total_emissions import annotate_total_emissions


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

    def test_each_action_sums_ges_from_itself_up_to_the_root(self):
        by_id = {action.pk: action.total_emissions for action in annotate_total_emissions(Action.objects.all())}

        self.assertEqual(
            by_id[self.root.pk],
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
            by_id[self.middle.pk],
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
            by_id[self.leaf.pk],
            {
                "ei": Decimal("111.000"),
                "ep": Decimal("222.000"),
                "etd": Decimal("333.000"),
                "eu": Decimal("444.000"),
                "eccs": Decimal("555.000"),
                "total": Decimal("555.000"),
            },
        )
