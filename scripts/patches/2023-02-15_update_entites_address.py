import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.db import transaction
from django.db.models import Q
from core.models import CarbureLot, Entity, Depot


@transaction.atomic
def update_entites_address():
    
    #get entities

    entities = Entity.objects.all()

    index = 0
    for entity in entities : 
        if entity.registered_address:
            index += 1
            print(" => "  + entity.registered_address )
    
    print(index)

if __name__ == "__main__":
    update_entites_address()
