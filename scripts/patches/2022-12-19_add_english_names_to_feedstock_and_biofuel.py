import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Biocarburant, MatierePremiere  # noqa: E402


def add_english_names_to_feedstock_and_biofuel():
    # feedstocks
    feedstock_file = open("front/public/locales/en/feedstocks.json")
    feedstock_translation = json.load(feedstock_file)
    feedstock_file.close()
    feedstocks = MatierePremiere.objects.all()

    for feedstock in feedstocks:
        feedstock.name_en = feedstock_translation.get(feedstock.code, "")

    MatierePremiere.objects.bulk_update(feedstocks, ["name_en"])

    # biofuels
    biofuel_file = open("front/public/locales/en/biofuels.json")
    biofuel_translation = json.load(biofuel_file)
    biofuel_file.close()
    biofuels = Biocarburant.objects.all()

    for biofuel in biofuels:
        biofuel.name_en = biofuel_translation.get(biofuel.code, "")

    Biocarburant.objects.bulk_update(biofuels, ["name_en"])


if __name__ == "__main__":
    add_english_names_to_feedstock_and_biofuel()
