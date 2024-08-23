import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity, LotTransaction


def try_assign_volumes():
    entities = Entity.objects.filter(entity_type__in=['Producteur', 'Trader'])
    stock = LotTransaction.objects.filter(carbure_client__in=entities, lot__status='Validated')

    for s in stock:
        # do we have children?
        children = LotTransaction.objects.filter(lot__parent_lot=s.lot)
        print('Found lot from %s' % (s.lot.added_by.name))
        if children.count() == 0:
            print('Setting remaining_volume back on %d' % (s.id))
            s.lot.remaining_volume = s.lot.volume
            s.lot.save()
        else:
            print('Found tx with children %d' % (s.id))

def main():
    try_assign_volumes()

if __name__ == '__main__':
    main()
