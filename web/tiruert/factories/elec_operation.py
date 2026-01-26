import factory
from factory import fuzzy

from tiruert.models import ElecOperation


class ElecOperationFactory(factory.django.DjangoModelFactory):
    """Factory for creating ElecOperation instances."""

    class Meta:
        model = ElecOperation

    type = fuzzy.FuzzyChoice(
        [
            ElecOperation.ACQUISITION_FROM_CPO,
            ElecOperation.CESSION,
            ElecOperation.TENEUR,
        ]
    )
    status = fuzzy.FuzzyChoice(
        [
            ElecOperation.PENDING,
            ElecOperation.ACCEPTED,
            ElecOperation.DECLARED,
        ]
    )
    quantity = fuzzy.FuzzyFloat(1_000.0, 10_000.0)
    credited_entity = None
    debited_entity = None

    @classmethod
    def create_credit(cls, entity, **kwargs):
        """Helper to create a credited operation for an entity."""
        defaults = {
            "type": ElecOperation.CESSION,
            "status": ElecOperation.ACCEPTED,
            "credited_entity": entity,
        }
        defaults.update(kwargs)
        return cls.create(**defaults)

    @classmethod
    def create_debit(cls, entity, **kwargs):
        """Helper to create a debited operation for an entity."""
        defaults = {
            "type": ElecOperation.CESSION,
            "status": ElecOperation.ACCEPTED,
            "debited_entity": entity,
        }
        defaults.update(kwargs)
        return cls.create(**defaults)

    @classmethod
    def create_teneur(cls, entity, status=ElecOperation.PENDING, **kwargs):
        """Helper to create a teneur operation debiting an entity."""
        defaults = {
            "type": ElecOperation.TENEUR,
            "status": status,
            "debited_entity": entity,
        }
        defaults.update(kwargs)
        return cls.create(**defaults)
