import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import ISCCScope

def load_scopes():
    scopes_filename = '%s/web/fixtures/csv/iscc_scopes.csv' % (os.environ['CARBURE_HOME'])
    with open(scopes_filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            ISCCScope.objects.update_or_create(scope=row[0], defaults={'description': row[1]})

def load_certificates():
    filename = '%s/web/fixtures/csv/Certificates_2020-09-21.csv' % (os.environ['CARBURE_HOME'])

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            print(row)

        #obj, created = MatierePremiere.objects.update_or_create(code=code, defaults={'name':name, 'description':'', 'compatible_alcool': compat_alcool, 'compatible_graisse': compat_graisse})

def main():
    load_scopes()
    # load_raw_materials()
    # load_certificates()
        
if __name__ == '__main__':
    main()
