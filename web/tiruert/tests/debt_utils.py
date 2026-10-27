from datetime import date

from django.db.models import Q

from core.models import Biocarburant, CarbureLot, DeclarationPeriod, Entity, MatierePremiere
from tiruert.models import Operation, TiruertDebt
from tiruert.services.balance import BalanceService
from tiruert.services.operation import OperationService
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


class DebtTestMixin:
    """Shared fixtures and helpers for the debt repayment tests."""

    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/entities_sites.json",
    ]

    @classmethod
    def setUpTestData(cls):
        today = date.today()
        DeclarationPeriod.objects.create(
            year=today.year,
            start_date=date(today.year, 1, 1),
            end_date=date(today.year, 12, 31),
            app=DeclarationPeriod.TIRUERT,
        )
        operators = Entity.objects.filter(entity_type=Entity.OPERATOR)
        cls.entity = operators.first()
        cls.other_entity = operators.exclude(id=cls.entity.id).first()
        cls.depot = Depot.objects.first()
        cls.biofuel = Biocarburant.objects.get(code="EMAG")
        cls.feedstock_conv = MatierePremiere.biofuel.filter(category="CONV").first()

    def create_lot(self, volume=1000, entity=None):
        """A lot credited to `entity` by an INCORPORATION operation of the same volume."""
        lot = CarbureLotFactory.create(
            carbure_client=entity or self.entity,
            feedstock=self.feedstock_conv,
            biofuel=self.biofuel,
            lot_status="ACCEPTED",
            delivery_type="BLENDING",
            volume=volume,
            ghg_total=12.5,
            carbure_delivery_site=self.depot,
        )
        OperationService.create_operations_from_lots(CarbureLot.objects.filter(id=lot.id))
        return lot

    def create_debt(self, lot, value, entity=None):
        return TiruertDebt.objects.create(
            type=TiruertDebt.VOLUME,
            value=value,
            entity=entity or self.entity,
            biofuel=self.biofuel,
            customs_category=MatierePremiere.CONV,
            lot=lot,
        )

    def lot_balance(self, lot, entity=None):
        entity = entity or self.entity
        operations = (
            Operation.objects.filter(biofuel=self.biofuel, customs_category=MatierePremiere.CONV)
            .filter(Q(credited_entity=entity) | Q(debited_entity=entity))
            .distinct()
        )
        balance = BalanceService.calculate_balance(
            operations,
            entity.id,
            BalanceService.GROUP_BY_LOT,
            "l",
            detail_filters={"lot_ids": [lot.id]},
        )
        return sum(entry["available_balance"] for entry in balance.values())

    def remaining(self, debt):
        return TiruertDebt.objects.with_remaining().get(id=debt.id).remaining
