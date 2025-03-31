import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Pays  # noqa: E402
from transactions.models import Airport  # noqa: E402

filename = "%s/web/fixtures/csv/airports.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        country = row[0]
        if country == "country":
            # header
            continue
        country = Pays.objects.get(code_pays=country)
        icao = row[1]
        name = row[2]
        city = row[3]
        coordinates = f"{row[4]},{row[5]}"
        is_eu_airport = row[6]
        obj, created = Airport.objects.update_or_create(
            icao_code=icao,
            defaults={
                "name": name,
                "city": city,
                "country": country,
                "site_type": "AIRPORT",
                "is_ue_airport": is_eu_airport,
                "gps_coordinates": coordinates,
                "is_enabled": True if is_eu_airport == "1" else False,
            },
        )
