import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from certificates.models import EntityISCCTradingCertificate, ProductionSiteCertificate


def check_entity_certificates():
    associated = EntityISCCTradingCertificate.objects.all().order_by('entity_id')
    for a in associated:
        print('ISCC Trading Cert', a.entity.id, a.certificate.certificate_id)
    psitecert = ProductionSiteCertificate.objects.filter(certificate_iscc__isnull=False).order_by('entity_id')
    for pc in psitecert:
        print('ProductionSite', pc.production_site.id, pc.certificate_iscc.certificate.certificate_id)

def main():
    check_entity_certificates()

if __name__ == '__main__':
    main()

