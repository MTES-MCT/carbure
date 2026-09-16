from decimal import Decimal

import factory
from factory import fuzzy

from core.models import Entity
from entity.factories.entity import EntityFactory
from traceability.models.action import Action
from traceability.models.action_status import ActionStatus
from transactions.factories.site import SiteFactory

from .material import MaterialFactory


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Action
        django_get_or_create = ("pos_id",)

    pos_id = factory.Faker("lexify", text="POS-????????????")
    holder = factory.SubFactory(EntityFactory, entity_type=Entity.HRS)
    industry = fuzzy.FuzzyChoice(Action.INDUSTRIES, getter=lambda x: x[0])
    type = fuzzy.FuzzyChoice(Action.TYPES, getter=lambda x: x[0])
    unit = factory.LazyAttribute(lambda o: Action.KG if o.type == Action.INIT else Action.MJ)
    working_date = factory.Faker("date_between", start_date="-2y", end_date="today")
    parent = None
    material = factory.SubFactory(MaterialFactory)
    quantity = factory.Faker("pydecimal", left_digits=4, right_digits=3, positive=True)
    site = factory.SubFactory(SiteFactory)
    shipping_date = factory.Faker("date_this_year")
    shipping_distance = factory.Faker("random_int", min=1, max=1000)
    shipping_method = fuzzy.FuzzyChoice(Action.SHIPPING_METHODS, getter=lambda x: x[0])
    ei = Decimal("0")
    ep = Decimal("0")
    etd = Decimal("0")
    eu = Decimal("0")
    eccs = Decimal("0")

    @factory.post_generation
    def status(self, create, extracted, **kwargs):
        if create:
            status = extracted or ActionStatus.PENDING
            ActionStatus.objects.get_or_create(action=self, status=status)
