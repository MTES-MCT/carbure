from traceability.models import Material
from transactions.models import Site


def material(_entity):
    return Material.objects.all()


def site(_entity):
    return Site.objects.all()
