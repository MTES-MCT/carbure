# pipenv run python scripts/patches/2023-07-25_generate_production_site_dc_number.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction
from core.models import ProductionSite


@transaction.atomic
def generate_dc_number():
    # recuperer tous les sites de productions
    production_sites = ProductionSite.objects.all()
    # pour chaque site de production, recuperer le numéro d'agrement s'il existe (dc reference) et créer le dc_number à partir de l'int apres FR_ et avant l'année
    for production_site in production_sites:
        # si le site de prod est null ou vide
        if not production_site.dc_reference:
            continue
        dc_reference = production_site.dc_reference
        dc_number = dc_reference.split("_")[1]
        print("dc_number géné ré: ", dc_number)
        # enregistrer le dc_number dans la base de données
        production_site.dc_number = dc_number
        # production_site.save()


generate_dc_number()
