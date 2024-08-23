import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *


def check_duplicates():
    lots_with_parent = CarbureLot.objects.filter(parent_lot__isnull=False)
    print('Found %d lots with parents' % (lots_with_parent.count()))
    for l in lots_with_parent:
        if l.parent_lot.carbure_client == l.carbure_client:
            if l.parent_lot.carbure_supplier == None and l.carbure_supplier != None and l.carbure_supplier != l.carbure_client:
                print('Odd. Lot %d client is same as child lot id %d (client %s)' % (l.parent_lot.id, l.id, l.carbure_client.name if l.carbure_client else None))
                print('Original producer %s vendor %s supplier %s (unknown supplier %s)' % (l.parent_lot.carbure_producer, l.parent_lot.carbure_vendor, l.parent_lot.carbure_supplier, l.parent_lot.unknown_supplier))
                print('Child lot producer %s vendor %s supplier %s (unknown supplier %s)' % (l.carbure_producer, l.carbure_vendor, l.carbure_supplier, l.unknown_supplier))
                l.parent_lot.carbure_client = l.carbure_supplier
                l.parent_lot.save()


if __name__ == '__main__':
    check_duplicates()
