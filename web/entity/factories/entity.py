import factory
from django.contrib.auth import get_user_model

from core.models import Entity, Pays

User = get_user_model()


class EntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entity

    class Params:
        company_name = factory.Faker("first_name")

    entity_type = factory.Iterator([choice[0] for choice in Entity.ENTITY_TYPES])

    name = factory.LazyAttribute(lambda obj: f"{dict(Entity.ENTITY_TYPES)[obj.entity_type]} - {obj.company_name}")
    parent_entity = None

    # Boolean capabilities
    has_mac = False
    has_trading = False
    has_stocks = False
    has_direct_deliveries = False
    has_elec = False
    has_saf = False

    # Contact and legal information
    legal_name = factory.LazyAttribute(lambda obj: f"{obj.name} SA")
    registration_id = "120087010"  # SIREN DGEC
    sustainability_officer_phone_number = factory.Faker("phone_number")
    sustainability_officer_email = factory.Faker("email")
    sustainability_officer = factory.Faker("name")

    # Address information
    registered_address = factory.Faker("address")
    registered_zipcode = factory.Faker("postcode")
    registered_city = factory.Faker("city")
    registered_country = factory.LazyFunction(lambda: Pays.objects.order_by("?").first())

    # Status flags
    is_enabled = True
    is_tiruert_liable = False
    is_red_ii = False

    # Other fields
    hash = ""
    default_certificate = ""
    notifications_enabled = True
    preferred_unit = Entity.UNIT_CHOICE[0][0]
    activity_description = factory.Faker("text", max_nb_chars=200)
    website = factory.Faker("url")
    vat_number = factory.Faker("lexify", text="FR????????????")
    accise_number = ""
