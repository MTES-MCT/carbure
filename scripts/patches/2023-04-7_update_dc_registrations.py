import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction
from django.db.models import Q
from core.models import ProductionSite, CarbureLot
from certificates.models import DoubleCountingRegistration
from api.v4.sanity_checks import bulk_sanity_checks


@transaction.atomic
def update_dc_registrations():
    dc_lots = CarbureLot.objects.filter(production_site_double_counting_certificate__isnull=False).exclude(
        production_site_double_counting_certificate__exact=""
    )

    dc_certificate_not_found = 0
    lot_without_valid_dc_certificate = 0

    for dc_lot in dc_lots:
        # 1 - on met à jour le site de production dans le certificat du lot
        dc_cert_id = dc_lot.production_site_double_counting_certificate
        dc_production_site = dc_lot.carbure_production_site
        try:
            dc_cert = DoubleCountingRegistration.objects.get(certificate_id=dc_cert_id)
            if dc_cert.production_site != dc_production_site:
                dc_cert.production_site = dc_production_site
                dc_cert.save()
        except:
            print(f"DC Certificate not found for lot {dc_lot} {dc_lot.delivery_date} {dc_lot.carbure_producer} ")
            dc_certificate_not_found += 1

    for dc_lot in dc_lots:
        # 2 - on récupere le certificat valide pour le site de production du lot et on le met à jour dans le lot s'il existe
        try:
            valid_certificate = DoubleCountingRegistration.objects.filter(
                production_site_id=dc_lot.carbure_production_site.id,
                valid_from__lt=dc_lot.delivery_date,
                valid_until__gte=dc_lot.delivery_date,
            ).first()
            if dc_lot.production_site_double_counting_certificate != valid_certificate.certificate_id:
                dc_lot.production_site_double_counting_certificate = valid_certificate.certificate_id
                dc_lot.save()
        except:
            print(f"not valid certificate found for {dc_lot}")
            lot_without_valid_dc_certificate += 1

    # 3 - Au cas où, on met à jour le site de production dans le certificat
    dc_production_sites = ProductionSite.objects.filter(eligible_dc=True)
    for production_site in dc_production_sites:
        certificate_id = production_site.dc_reference
        try:
            certificate = DoubleCountingRegistration.objects.get(certificate_id=certificate_id)
            certificate.production_site = production_site
            certificate.save()
        except:
            print("DC Certificate not found")

    bulk_sanity_checks(dc_lots)
