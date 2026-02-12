import factory
from factory import fuzzy

from certificates.models import ProductionSiteCertificate
from core.models import Biocarburant, MatierePremiere
from entity.factories.entity import EntityFactory
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.factories.certificate import EntityCertificateFactory
from transactions.factories.site import SiteFactory
from transactions.models.production_site import ProductionSite


class ProductionSiteFactory(SiteFactory):
    """Factory for ProductionSite model with production site-specific fields."""

    class Meta:
        model = ProductionSite

    site_type = fuzzy.FuzzyChoice(ProductionSite.PRODUCTION_SITE_TYPES, getter=lambda x: x[0])
    date_mise_en_service = factory.Faker("date")
    ges_option = fuzzy.FuzzyChoice(ProductionSite.GES_OPTIONS, getter=lambda x: x[0])
    eligible_dc = factory.Faker("boolean")
    dc_number = factory.Faker("lexify", text="????????????")
    dc_reference = factory.Faker("lexify", text="????????????")
    manager_name = factory.Faker("name")
    manager_phone = factory.Faker("phone_number")
    manager_email = factory.Faker("email")


class ProductionSiteInputFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSiteInput

    production_site = factory.SubFactory(ProductionSiteFactory)
    matiere_premiere = factory.Iterator(MatierePremiere.biofuel.all())
    status = "Valid"


class ProductionSiteOutputFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSiteOutput

    production_site = factory.SubFactory(ProductionSiteFactory)
    biocarburant = factory.Iterator(Biocarburant.objects.all())
    status = "Valid"


class ProductionSiteCertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSiteCertificate

    entity = factory.SubFactory(EntityFactory)
    production_site = factory.SubFactory(ProductionSiteFactory)
    certificate = factory.SubFactory(EntityCertificateFactory)
