import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *

if __name__ == '__main__':
    entites_with_stock = CarbureStock.objects.values('carbure_client').distinct()
    for e in entites_with_stock:
        entity = Entity.objects.get(id=e['carbure_client'])
        entity.has_stocks = True
        entity.save()
