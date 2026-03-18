import factory
from django.utils import timezone
from factory import fuzzy
from matplotlib.dates import relativedelta

from core.models import EntityCertificate, GenericCertificate
from entity.factories.entity import EntityFactory


class GenericCertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GenericCertificate

    certificate_id = factory.Faker("lexify", text="??????????")
    certificate_type = fuzzy.FuzzyChoice(GenericCertificate.CERTIFICATE_TYPES, getter=lambda x: x[0])
    certificate_holder = factory.Faker("company")
    certificate_issuer = factory.Faker("company")
    address = factory.Faker("address")
    valid_from = factory.Faker("date_between", start_date="-2y", end_date="today")
    valid_until = factory.LazyAttribute(lambda obj: obj.valid_from + relativedelta(years=1))
    download_link = factory.Faker("url")
    scope = '"SCOPE_TEST"'
    input = None
    output = None
    last_status_update = timezone.localdate()
    status = GenericCertificate.VALID


class EntityCertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EntityCertificate

    certificate = factory.SubFactory(GenericCertificateFactory)
    entity = factory.SubFactory(EntityFactory)
    has_been_updated = factory.Faker("boolean")
    checked_by_admin = factory.Faker("boolean")
    rejected_by_admin = factory.Faker("boolean")
