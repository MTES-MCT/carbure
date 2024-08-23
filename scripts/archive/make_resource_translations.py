import json
import os

import django
import environ
from django.db.models import F

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    TEST=(bool, False),
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()
from core.models import Biocarburant, MatierePremiere, Pays

queries = {
    "feedstocks.json": MatierePremiere.objects.all()
    .annotate(value=F("code"), label=F("name"))
    .values("value", "label")
    .order_by("value"),
    "biofuels.json": Biocarburant.objects.all()
    .annotate(value=F("code"), label=F("name"))
    .values("value", "label")
    .order_by("value"),
    "countries.json": Pays.objects.all()
    .annotate(value=F("code_pays"), label=F("name"), label_en=F("name_en"))
    .values("value", "label", "label_en")
    .order_by("value"),
}


def make_translation_file(filename, query, lang):
    translation = {}

    for result in query:
        translation[result["value"]] = result["label_en"] if lang == "en" and "label_en" in result else result["label"]

    file_path = os.path.join(env("CARBURE_HOME"), "front/public/locales", lang, filename)
    file = open(file_path, "w+")
    serialized = json.dumps(translation, indent=2, ensure_ascii=False)

    file.write(serialized)
    file.close()


for filename, query in queries.items():
    for lang in ("fr", "en"):
        make_translation_file(filename, query, lang)
