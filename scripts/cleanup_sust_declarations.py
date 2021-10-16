import os
import django
import argparse
from django.db.models import Sum, Count, Min

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *

def fix_declaration_duplicates():
    summary = SustainabilityDeclaration.objects.values('entity', 'period').annotate(count=Count('period'))
    for d in summary:
        if d['count'] > 1:
            print(d)
            # keep only the first one
            declarations = SustainabilityDeclaration.objects.filter(entity_id=d['entity'], period=d['period']).order_by('id')
            min_id = declarations[0].id
            to_delete = declarations.exclude(id=min_id)
            to_delete.delete()

if __name__ == '__main__':
    fix_declaration_duplicates()
