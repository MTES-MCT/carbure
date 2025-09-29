import factory
from factory import fuzzy

from certificates.models import ProductionSiteCertificate
from core.models import Biocarburant, MatierePremiere
from entity.factories.entity import EntityFactory
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.factories.certificate import EntityCertificateFactory
from transactions.factories.site import SiteFactory
from transactions.models.production_site import ProductionSite


class ProductionSiteInputFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSiteInput

    production_site = factory.SubFactory(SiteFactory)
    matiere_premiere = factory.Iterator(MatierePremiere.objects.all())
    status = "Valid"


class ProductionSiteOutputFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSiteOutput

    production_site = factory.SubFactory(SiteFactory)
    biocarburant = factory.Iterator(Biocarburant.objects.all())
    status = "Valid"


class ProductionSiteCertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSiteCertificate

    entity = factory.SubFactory(EntityFactory)
    production_site = factory.SubFactory(SiteFactory)
    certificate = factory.SubFactory(EntityCertificateFactory)


class ProductionSiteFactory(SiteFactory):
    class Meta:
        model = ProductionSite

    site_type = fuzzy.FuzzyChoice(ProductionSite.PRODUCTION_SITE_TYPES, getter=lambda x: x[0])
