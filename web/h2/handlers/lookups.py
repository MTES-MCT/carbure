from core.models import GenericCertificate
from traceability.models import Industry, Material, T, Tag
from transactions.models import Site


def material(_entity):
    return Material.objects.filter(T(Tag.INDUSTRY, Industry.H2))


def site(entity):
    return Site.objects.filter(site_type=Site.H2_REFUELING_STATION, created_by=entity)


def certificate(_entity):
    return GenericCertificate.objects.filter(certificate_type=GenericCertificate.CERTIFHY).order_by("certificate_id")
