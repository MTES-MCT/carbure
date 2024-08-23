import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot


def delete_broken_bso_lots():
    lots = CarbureLot.objects.filter(
        transport_document_reference__in=dae_list, carbure_client__name="Bioenergie du Sud-Ouest"
    )

    lots.delete()


dae_list = (
    "002218",
    "002221",
    "002217",
    "002219",
    "002220",
    "002222",
    "002223",
    "002224",
    "002225",
    "002226",
    "002227",
    "002228",
    "002229",
    "002230",
    "002231",
    "002233",
    "002232",
    "002234",
    "002235",
    "002237",
    "002238",
    "002239",
    "002240",
    "002241",
    "002242",
    "002243",
    "002244",
    "002245",
    "002246",
    "002249",
    "002247",
    "002248",
    "002252",
    "002254",
    "002255",
    "002256",
    "002258",
    "002259",
    "002260",
    "002236",
    "002263",
    "002265",
    "002266",
    "002268",
    "002269",
    "002270",
    "002271",
    "002273",
    "002274",
    "002250",
    "002251",
    "002262",
    "002264",
    "002272",
    "002275",
    "002276",
    "002277",
    "002278",
    "002253",
    "002257",
    "002261",
)


if __name__ == "__main__":
    delete_broken_bso_lots()
