import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Pays  # noqa: E402
from transactions.models import Site as Depot  # noqa: E402

filename = "%s/web/fixtures/csv/depots.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        name = row[0]
        depot_id = row[1]
        city = row[2]
        country = row[3]
        if city == "Ville":
            continue
        country_obj = Pays.objects.get(code_pays=country)
        obj, created = Depot.objects.update_or_create(
            depot_id=depot_id, defaults={"name": name, "city": city, "country": country_obj}
        )
