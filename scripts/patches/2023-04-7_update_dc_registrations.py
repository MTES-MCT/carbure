import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction  # noqa: E402

from certificates.models import DoubleCountingRegistration  # noqa: E402
from core.models import CarbureLot, ProductionSite  # noqa: E402
from transactions.sanity_checks.sanity_checks import bulk_sanity_checks  # noqa: E402


@transaction.atomic
def update_dc_registrations():
    dc_lots = CarbureLot.objects.filter(production_site_double_counting_certificate__isnull=False).exclude(
        production_site_double_counting_certificate__exact=""
    )
    dc_certificate_not_found = 0
    for dc_lot in dc_lots:
        # 1 - on met à jour le site de production dans le certificat du lot
        dc_cert_id = dc_lot.production_site_double_counting_certificate
        dc_production_site = dc_lot.carbure_production_site
        try:
            dc_cert = DoubleCountingRegistration.objects.get(certificate_id=dc_cert_id)
            if dc_cert.production_site != dc_production_site:
                dc_cert.production_site = dc_production_site
                dc_cert.save()
                print(f"Production site {dc_production_site} associate with DC certificate {dc_cert_id}")
        except:
            # print(f"DC Certificate not found for lot {dc_lot} {dc_lot.delivery_date} {dc_lot.carbure_producer} ")
            dc_certificate_not_found = dc_certificate_not_found + 1
    print(f"DC Certificate not found for {dc_certificate_not_found} lots")

    # 2 - on récupere le certificat valide pour le site de production du lot et on le met à jour dans le lot s'il existe
    lot_without_valid_dc_certificate = 0
    for dc_lot in dc_lots:
        try:
            valid_certificate = DoubleCountingRegistration.objects.filter(
                production_site_id=dc_lot.carbure_production_site.id,
                valid_from__lt=dc_lot.delivery_date,
                valid_until__gte=dc_lot.delivery_date,
            ).first()
            if dc_lot.production_site_double_counting_certificate != valid_certificate.certificate_id:
                dc_lot.production_site_double_counting_certificate = valid_certificate.certificate_id
                dc_lot.save()
                print(f"Valid DC certificate {valid_certificate.certificate_id} found for {dc_lot}")
        except:
            print(f"not valid certificate found for {dc_lot}")
            lot_without_valid_dc_certificate += 1

    print(f"lots without valid dc certificate: {lot_without_valid_dc_certificate}")

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
