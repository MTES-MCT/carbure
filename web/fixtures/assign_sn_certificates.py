import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from certificates.models import EntitySNTradingCertificate, SNCertificate
from core.models import Entity

user_said_yes = lambda q: input(q).lower().strip()[0] == "y"


def try_assign_sn_certificates():
    certificates = SNCertificate.objects.all()
    for cert in certificates:
        assigned = EntitySNTradingCertificate.objects.filter(certificate=cert)
        if assigned.count() == 0:
            # try to find entity to assign
            matching_entity = Entity.objects.filter(name__icontains=cert.certificate_holder)
            if matching_entity.count() > 0:
                if matching_entity.count() == 1:
                    EntitySNTradingCertificate.objects.create(entity=matching_entity[0], certificate=cert)
            else:
                # try approximate match
                approx_matching = Entity.objects.filter(name__icontains=cert.certificate_holder[0:6])
                if approx_matching.count() > 0:
                    print("Found approx matching for %s:" % (cert.certificate_holder))
                    for m in approx_matching:
                        print(m)
                        if user_said_yes("Confirm match?"):
                            print("YES")
                            EntitySNTradingCertificate.objects.create(entity=m, certificate=cert)
                        else:
                            print("NO")
                else:
                    print("Could not find match for %s" % (cert.certificate_holder))


def main():
    try_assign_sn_certificates()


if __name__ == "__main__":
    main()
