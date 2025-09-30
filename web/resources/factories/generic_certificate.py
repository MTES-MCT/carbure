import factory
from factory import fuzzy
from matplotlib.dates import relativedelta

from core.models import GenericCertificate


class GenericCertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GenericCertificate

    certificate_id = factory.Faker("lexify", text="????????????")
    certificate_type = fuzzy.FuzzyChoice(GenericCertificate.CERTIFICATE_TYPES)
    certificate_holder = factory.Faker("company")
    certificate_issuer = factory.Faker("company")
    address = factory.Faker("address")
    valid_from = factory.Faker("date_between", start_date="-2y", end_date="today")
    valid_until = factory.LazyAttribute(lambda obj: obj.valid_from + relativedelta(years=1))
    download_link = factory.Faker("url")
    scope = '"SCOPE_TEST"'
    input = None
    output = None
