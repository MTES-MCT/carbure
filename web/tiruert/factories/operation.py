import factory
from factory import fuzzy

from core.models import Biocarburant, MatierePremiere
from tiruert.models import Operation, OperationDetail
from transactions.factories import CarbureLotFactory
from transactions.models import Depot


class OperationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Operation instances."""

    class Meta:
        model = Operation

    type = fuzzy.FuzzyChoice(
        [
            Operation.INCORPORATION,
            Operation.MAC_BIO,
            Operation.LIVRAISON_DIRECTE,
            Operation.CESSION,
            Operation.TENEUR,
            Operation.TRANSFERT,
            Operation.EXPORTATION,
            Operation.EXPEDITION,
        ]
    )
    status = fuzzy.FuzzyChoice(
        [
            Operation.DRAFT,
            Operation.PENDING,
            Operation.ACCEPTED,
            Operation.VALIDATED,
            Operation.REJECTED,
        ]
    )
    customs_category = factory.LazyAttribute(lambda _: MatierePremiere.CONV)
    biofuel = factory.LazyAttribute(lambda _: Biocarburant.objects.first())
    renewable_energy_share = 1.0

    # Nullable fields - can be overridden in tests
    credited_entity = None
    debited_entity = None
    from_depot = None
    to_depot = factory.LazyAttribute(lambda _: Depot.objects.first())
    export_country = None
    export_recipient = ""  # CharField with blank=True, not null=True
    validation_date = None
    durability_period = None

    @classmethod
    def create_with_entity(cls, entity, **kwargs):
        """Helper to create operation with credited_entity set."""
        return cls.create(credited_entity=entity, **kwargs)

    @classmethod
    def create_incorporation(cls, entity, depot=None, **kwargs):
        """Helper to create INCORPORATION operation (auto-accepted)."""
        if depot is None:
            depot = Depot.objects.first()
        defaults = {
            "type": Operation.INCORPORATION,
            "status": Operation.VALIDATED,
            "customs_category": MatierePremiere.CONV,
            "credited_entity": entity,
            "debited_entity": None,
            "from_depot": None,
            "to_depot": depot,
        }
        defaults.update(kwargs)
        return cls.create(**defaults)

    @classmethod
    def create_mac_bio(cls, entity, depot=None, **kwargs):
        """Helper to create MAC_BIO operation (auto-accepted)."""
        if depot is None:
            depot = Depot.objects.first()
        return cls.create(
            type=Operation.MAC_BIO,
            status=Operation.VALIDATED,
            customs_category=MatierePremiere.CONV,
            credited_entity=entity,
            debited_entity=None,
            from_depot=None,
            to_depot=depot,
            **kwargs,
        )

    @classmethod
    def create_livraison_directe(cls, entity, depot=None, **kwargs):
        """Helper to create LIVRAISON_DIRECTE operation (auto-accepted)."""
        if depot is None:
            depot = Depot.objects.first()
        return cls.create(
            type=Operation.LIVRAISON_DIRECTE,
            status=Operation.VALIDATED,
            customs_category=MatierePremiere.CONV,
            credited_entity=entity,
            debited_entity=None,
            from_depot=None,
            to_depot=depot,
            **kwargs,
        )

    @classmethod
    def create_cession(cls, debited_entity, credited_entity, depot=None, status=Operation.PENDING, **kwargs):
        """Helper to create CESSION operation."""
        if depot is None:
            depot = Depot.objects.first()
        return cls.create(
            type=Operation.CESSION,
            status=status,
            customs_category=MatierePremiere.CONV,
            debited_entity=debited_entity,
            credited_entity=credited_entity,
            to_depot=depot,
            **kwargs,
        )


class OperationDetailFactory(factory.django.DjangoModelFactory):
    """Factory for creating OperationDetail instances."""

    class Meta:
        model = OperationDetail

    operation = factory.SubFactory(OperationFactory)
    lot = factory.SubFactory(CarbureLotFactory)
    volume = fuzzy.FuzzyFloat(100.0, 5000.0)
    emission_rate_per_mj = fuzzy.FuzzyFloat(1.0, 20.0)

    @classmethod
    def create_for_operation(cls, operation, lot=None, **kwargs):
        """Helper to create OperationDetail for existing operation."""
        if lot is None:
            lot = CarbureLotFactory.create()
        return cls.create(operation=operation, lot=lot, **kwargs)
