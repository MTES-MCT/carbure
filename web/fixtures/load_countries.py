import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Pays  # noqa: E402

filename = "%s/web/fixtures/csv/countries.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=";", quotechar='"')
    for row in reader:
        code_pays = row[0]
        if code_pays == "code_pays":
            # header
            continue

        name_fr = row[1]
        if len(row) == 3:
            name_en = name_fr
            is_in_europe = True if row[2] == "1" else False
        else:
            name_en = row[2]
            is_in_europe = True if row[3] == "1" else False

        obj, created = Pays.objects.update_or_create(
            code_pays=code_pays, defaults={"name": name_fr, "name_en": name_en, "is_in_europe": is_in_europe}
        )
