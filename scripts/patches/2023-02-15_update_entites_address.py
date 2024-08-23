import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction

from core.models import Entity


@transaction.atomic
def update_entites_address():

    entity = Entity.objects.get(id=126)
    entity.registered_address = "48 Boulevard de l'Europe"
    entity.registered_zipcode = "59600"
    entity.registered_city = "Maubeuge"
    entity.registered_country = "France"
    entity.save()


    entity = Entity.objects.get(id=132)
    entity.registered_address = "Jafza 14,"
    entity.registered_zipcode = "LB-14303"
    entity.registered_city = "Dubai"
    entity.registered_country = "United Arab Emirates"
    entity.save()

    entity = Entity.objects.get(id=26)
    entity.registered_address = "Immeuble Spring - 20, rue Paul Héroult"
    entity.registered_zipcode = "92000"
    entity.registered_city = "NANTERRE"
    entity.registered_country = "France"
    entity.save()

    entity = Entity.objects.get(id=128)
    entity.registered_address = "20, rue Paul Héroult"
    entity.registered_zipcode = "92000"
    entity.registered_city = "NANTERRE"
    entity.registered_country = "France"
    entity.save()

    entity = Entity.objects.get(id=88)
    entity.registered_address = "POL IND  ALCES C/MENCIA PARC M80"
    entity.registered_zipcode = "13600"
    entity.registered_city = "ALCAZAR DE SAN JUAN"
    entity.registered_country = "ES"
    entity.save()


    entity = Entity.objects.get(id=88)
    entity.registered_address = "POL IND  ALCES C/MENCIA PARC M80"
    entity.registered_zipcode = "13600"
    entity.registered_city = "ALCAZAR DE SAN JUAN"
    entity.registered_country = "ES"
    entity.save()


    entity = Entity.objects.get(id=129)
    entity.registered_address = "Rue du Rhone 50,"
    entity.registered_zipcode = "1204"
    entity.registered_city = "Geneva"
    entity.registered_country = "Switzerland"
    entity.save()


    entity = Entity.objects.get(id=131)
    entity.registered_address = "Ketenislaan 3"
    entity.registered_zipcode = "9130"
    entity.registered_city = "Kallo"
    entity.registered_country = "Belgium"
    entity.save()

    entity = Entity.objects.get(id=141)
    entity.registered_address = "9, Avenue d'Ostende"
    entity.registered_zipcode = "98000"
    entity.registered_city = "Monaco"
    entity.registered_country = "Monaco"
    entity.save()

    entity = Entity.objects.get(id=35)
    entity.registered_address = "Rue André et Guy Picoty - BP1"
    entity.registered_zipcode = "23300"
    entity.registered_city = "LA SOUTERRAINE"
    entity.registered_country = "France"
    entity.save()

    entity = Entity.objects.get(id=105)
    entity.registered_address = "C/méndez Alvaro Nº44"
    entity.registered_zipcode = "28045"
    entity.registered_city = "Madrid"
    entity.registered_country = "Spain"
    entity.save()

    entity = Entity.objects.get(id=61)
    entity.registered_address = "11 rue Pasteur "
    entity.registered_zipcode = "02390"
    entity.registered_city = "ORIGNY-SAINTE-BENOITE"
    entity.registered_country = "France"
    entity.save()

    entity = Entity.objects.get(id=95)
    entity.registered_address = "2 place Jean Millier - La Défense 6,"
    entity.registered_zipcode = "92400"
    entity.registered_city = "Courbevoie"
    entity.registered_country = "France"
    entity.save()

    entity = Entity.objects.get(id=64)
    entity.registered_address = "10 route de l'Aéroport (case postale 276)"
    entity.registered_zipcode = "1215 G"
    entity.registered_city = "Geneva 15 "
    entity.registered_country = "Switzerland"
    entity.save()

    entity = Entity.objects.get(id=98)
    entity.registered_address = "Riva Paradiso, 2"
    entity.registered_zipcode = "6900"
    entity.registered_city = "Paradiso"
    entity.registered_country = "Switzerland"
    entity.save()

    entity = Entity.objects.get(id=51)
    entity.registered_address = "8 rue Ellenhard"
    entity.registered_zipcode = "67000"
    entity.registered_city = "STRASBOURG"
    entity.registered_country = "France"
    entity.save()

if __name__ == "__main__":
    update_entites_address()
