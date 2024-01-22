import argparse
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction
from core.models import MatierePremiere


@transaction.atomic
def rename_alcool_pur_marc_raisin(id, name, code):
    try:
        feedstock = MatierePremiere.objects.get(id=id)
    except:
        print(f"Feedstock {id} not found")
        return
    print(f"Feedstock {feedstock.code} updated by {name}")
    feedstock.name = name
    feedstock.code = code
    feedstock.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update feedstock --id --name --code")
    parser.add_argument("--id", dest="id", action="store", default=None, help="Feedstock ID")
    parser.add_argument("--name", dest="name", action="store", default=None, help="Feedstock name")
    parser.add_argument("--code", dest="code", action="store", default=None, help="Feedstock code")
    args = parser.parse_args()
    rename_alcool_pur_marc_raisin(id=args.id, name=args.name, code=args.code)
