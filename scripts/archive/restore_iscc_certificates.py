import datetime
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from certificates.models import EntityISCCTradingCertificate, ISCCCertificate, ProductionSiteCertificate  # noqa: E402
from core.models import Entity  # noqa: E402
from producers.models import ProductionSite  # noqa: E402

entity_certs = [
    (58, "EU-ISCC-Cert-DE105-82948108"),
    (7, "EU-ISCC-Cert-PL214-71150720"),
    (65, "EU-ISCC-Cert-PL214-47360320"),
    (12, "EU-ISCC-Cert-PL214-69190420"),
    (6, "EU-ISCC-Cert-DE105-81332476"),
    (54, "EU-ISCC-Cert-DE105-81969806"),
    (3, "EU-ISCC-Cert-DE105-86620902"),
    (81, "EU-ISCC-Cert-DE105-83388707"),
    (80, "EU-ISCC-Cert-DE105-83412407"),
    (79, "EU-ISCC-Cert-DE105-83416607"),
    (8, "EU-ISCC-Cert-DE105-82925108"),
    (58, "EU-ISCC-Cert-DE105-82948109"),
    (78, "EU-ISCC-Cert-DE100-11202020"),
    (84, "EU-ISCC-Cert-DE100-10032021"),
    (83, "EU-ISCC-Cert-PL214-51870320"),
    (86, "EU-ISCC-Cert-DE105-82391908"),
    (86, "EU-ISCC-Cert-DE105-81899912"),
    (82, "EU-ISCC-Cert-DE105-83050308"),
    (87, "EU-ISCC-Cert-DE100-17442020"),
    (58, "EU-ISCC-Cert-DE105-80820921"),
    (66, "EU-ISCC-Cert-DE100-11742021"),
    (90, "EU-ISCC-Cert-DE105-81648310"),
    (66, "EU-ISCC-Cert-DE100-11742020"),
    (92, "EU-ISCC-Cert-DE105-82959708"),
    (64, "EU-ISCC-Cert-DE100-09212020"),
    (64, "DE-B-BLE-BM-10-100-27120020"),
    (67, "EU-ISCC-Cert-DE100-14052020"),
    (97, "EU-ISCC-Cert-ES216-202110751"),
    (94, "EU-ISCC-Cert-DE100-12982020"),
    (95, "EU-ISCC-Cert-PL214-58470920"),
    (91, "EU-ISCC-Cert-PL214-18461220"),
]

psite_certs = [
    (17, "EU-ISCC-Cert-DE105-81969806"),
    (36, "EU-ISCC-Cert-PL214-47360320"),
    (24, "EU-ISCC-Cert-DE105-80820921"),
    (46, "EU-ISCC-Cert-DE105-81899912"),
    (45, "EU-ISCC-Cert-DE105-82391908"),
    (48, "EU-ISCC-Cert-DE100-10032021"),
    (37, "EU-ISCC-Cert-DE105-83416607"),
    (16, "EU-ISCC-Cert-DE105-82925108"),
    (49, "EU-ISCC-Cert-DE100-11742021"),
    (10, "EU-ISCC-Cert-PL214-71150720"),
    (12, "EU-ISCC-Cert-PL214-71150720"),
    (33, "EU-ISCC-Cert-PL214-71150720"),
    (35, "EU-ISCC-Cert-PL214-71150720"),
    (34, "EU-ISCC-Cert-PL214-71150720"),
    (39, "EU-ISCC-Cert-DE105-83388707"),
    (38, "EU-ISCC-Cert-DE105-83412407"),
    (11, "EU-ISCC-Cert-DE105-86620902"),
    (28, "EU-ISCC-Cert-PL214-69190420"),
    (51, "EU-ISCC-Cert-DE100-12982020"),
    (53, "EU-ISCC-Cert-PL214-58470920"),
]


def check_entity_certificates():
    twoyearsago = datetime.datetime.now() - datetime.timedelta(days=730)
    for entity_id, certificate in entity_certs:
        entity = Entity.objects.get(id=entity_id)
        print("Adding %s with certificate_id %s" % (entity.name, certificate))
        found = ISCCCertificate.objects.filter(certificate_id=certificate, valid_until__gt=twoyearsago)
        if found.count() > 1:
            print("multiple matches")
            iscc = found[0]
            continue
        else:
            iscc = found[0]
            print("Found certif for %s" % (iscc.certificate_holder))
            EntityISCCTradingCertificate.objects.update_or_create(entity=entity, certificate=iscc)
            print("Done")
    for psite_id, certificate in psite_certs:
        psite = ProductionSite.objects.get(id=psite_id)
        iscc = EntityISCCTradingCertificate.objects.get(
            entity=psite.producer, certificate__certificate_id=certificate, certificate__valid_until__gt=twoyearsago
        )
        ProductionSiteCertificate.objects.update_or_create(
            entity=psite.producer, production_site=psite, type="ISCC", certificate_iscc=iscc
        )


def main():
    check_entity_certificates()


if __name__ == "__main__":
    main()
