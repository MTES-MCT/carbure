import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GHGValues, MatierePremiere, Biocarburant

filename = '%s/web/fixtures/ghg_values.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(reader)
    for row in reader:
        # header code_biocarburant,biocarburant,code_matiere_premiere,matiere_premiere,condition,eec_typical,eec_default,ep_typical,ep_default,etd_typical,etd_default
        code_biocarburant = row[0]
        biocarburant = row[1]
        code_mp = row[2]
        mp = row[3]
        condition = row[4]
        eec_typical = row[5]
        eec_default = row[6]
        ep_typical = row[7]
        ep_default = row[8]
        etd_typical = row[9]
        etd_default = row[10]

        # get foreign keys
        if code_mp != '':
            try:
                mp = MatierePremiere.objects.get(code=code_mp)
            except:
                print('Could not find matiere premiere with code %s'  % (code_mp))
                print(row)
                continue
        else:
            mp = None
        try:
            bc = Biocarburant.objects.get(code=code_biocarburant)
        except:
            print('Could not find biocarburant with code %s'  % (code_biocarburant))
            print(row)            
            continue

        # typical values
        d = {
            'eec_typical':eec_typical,
            'eec_default':eec_default,
            'ep_typical':ep_typical,
            'ep_default':ep_default,
            'etd_typical':etd_typical,
            'etd_default':etd_default
        }
        obj, created = GHGValues.objects.update_or_create(matiere_premiere=mp, biocarburant=bc, condition=condition, defaults=d)
        
