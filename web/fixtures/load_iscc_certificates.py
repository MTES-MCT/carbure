import sys, os
import django
import csv
import calendar
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import ISCCScope, ISCCCertificate, ISCCCertificateScope, ISCCCertificateRawMaterial

scopes = {}
today = datetime.date.today()
CSV_FOLDER = '/tmp'

def fix_nulls(s):
    for line in s:
        yield line.replace('\0', ' ')

def load_scopes():
    scopes_filename = '%s/web/fixtures/csv/iscc_scopes.csv' % (os.environ['CARBURE_HOME'])
    with open(scopes_filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            obj, created = ISCCScope.objects.update_or_create(scope=row[0], defaults={'description': row[1]})
            scopes[row[0]] = obj

def bulk_save(bulk_crt, bulk_scopes, bulk_rm):
    ISCCCertificate.objects.bulk_create(bulk_crt)

    last_100 = ISCCCertificate.objects.all().order_by('-id')[:100]
    objs = list(reversed(last_100))
    
    # 2: attach scopes and raw materials
    bulk_scopes_insert = []
    for i, crt_scopes in enumerate(bulk_scopes):
        crt = objs[i]
        for scope in crt_scopes.split(','):
            scope = scope.strip()
            if not scope:
                continue
            if scope not in scopes:
                if crt.valid_until > today:
                    print('Could not find scope [%s] in scopes' % (scope))
                continue
            bulk_scopes_insert.append(ISCCCertificateScope(certificate=crt, scope=scopes[scope]))
    res = ISCCCertificateScope.objects.bulk_create(bulk_scopes_insert)

    bulk_rm_insert = []
    for i, crt_rm in enumerate(bulk_rm):
        crt = objs[i]
        for raw_material in crt_rm.split(','):
            bulk_rm_insert.append(ISCCCertificateRawMaterial(certificate=crt, raw_material=raw_material.strip()))
    ISCCCertificateRawMaterial.objects.bulk_create(bulk_rm_insert)
    
            
def load_certificates():
    try:
        last_crt = ISCCCertificate.objects.latest('id')
    except:
        last_crt = None

    filename = '%s/Certificates_%s.csv' % (CSV_FOLDER, today.strftime('%y-%m-%d'))

    csvfile = open(filename, 'r')
    reader = csv.DictReader(fix_nulls(csvfile), delimiter=',', quotechar='"')
    i = 0
    bulk_crt = []
    bulk_scopes = []
    bulk_rm = []
    for row in reader:
        i += 1
            
        # 1: create certificate
        try:
            vf = row['valid_from'].split('.')
            valid_from = datetime.datetime(year=2000 + int(vf[2]), month=int(vf[1]), day=int(vf[0]))
        except:
            valid_from = datetime.datetime(year=1970, month=1, day=1)

        try:
            vu = row['valid_until'].split('.')
            valid_until = datetime.datetime(year=2000 + int(vu[2]), month=int(vu[1]), day=int(vu[0]))
        except:
            valid_from = datetime.datetime(year=1970, month=1, day=1)            
        d = {'certificate_holder': row['certificate_holder'],
             'addons': row['addons'],
             'valid_from': valid_from,
             'valid_until': valid_until,
             'issuing_cb': row['issuing_cb'],
             'location': row['map'],
             'certificate_id': row['certificate']
        }
        # print(d)
        certificate = ISCCCertificate(**d)
        bulk_crt.append(certificate)
        bulk_scopes.append(row['scope'])
        bulk_rm.append(row['raw_material'])
        if i % 100 == 0:
            print('loading certificate %d' % (i))
            bulk_save(bulk_crt, bulk_scopes, bulk_rm)
            bulk_crt = []
            bulk_scopes = []
            bulk_rm = []
        continue
    bulk_save(bulk_crt, bulk_scopes, bulk_rm)
    print('loading certificate %d' % (i))    
    csvfile.close()
    if i > 10000:
        if last_crt:
            nb_deleted, _ = ISCCCertificate.objects.filter(id__lte=last_crt.id).delete()
            print('%d objects created, %d certificates deleted' % (i, nb_deleted))
    return
        

        
def main():
    load_scopes()
    # load_raw_materials()
    load_certificates()
        
if __name__ == '__main__':
    main()
