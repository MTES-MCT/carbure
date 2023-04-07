import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction
from django.db.models import Q
from core.models import ProductionSite
from certificates.models import DoubleCountingRegistration


@transaction.atomic
def update_dc_registrations():
    print("TEST")
    # dc_production_sites = ProductionSite.objects.filter(dc_reference__isnull=False, dc_reference__regex=r"\S+")
    # for production_site in dc_production_sites:
    #     certificate_id = production_site.dc_reference
    #     try:
    #         certificate = DoubleCountingRegistration.objects.get(certificate_id=certificate_id)
    #         certificate.production_site = production_site
    #         certificate.save()
    #     except:
    #         print("DC Certificate not found")
