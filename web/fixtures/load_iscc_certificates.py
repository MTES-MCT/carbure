import sys, os
import django
import csv
import calendar
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import ISCCScope, ISCCCertificate, ISCCCertificateScope, ISCCCertificateRawMaterial

VALID_SCOPES = {}
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
            VALID_SCOPES[row[0]] = obj

def save_certificate(certificate_id, holder, valid_from, valid_until, details):
    if isinstance(valid_until, datetime.datetime):
        until = valid_until.date()
    else:
        until = valid_until
    if until <= today:
        # the certificate is invalid, do not try to update its valid_until date
        try:
            certificate, created = ISCCCertificate.objects.update_or_create(certificate_id=certificate_id, valid_from=valid_from, valid_until=valid_until, certificate_holder=holder, defaults=details)
            return certificate
        except Exception as e:
            print('')
            print(e)
            print(certificate_id)
            print(ISCCCertificate.objects.filter(certificate_id=certificate_id, valid_from=valid_from, valid_until=valid_until))
    else:
        # the certificate is valid, try to update its valid_until date
        try:
            details['valid_until'] = valid_until
            certificate, created = ISCCCertificate.objects.update_or_create(certificate_id=certificate_id, valid_from=valid_from, certificate_holder=holder, defaults=details)
            return certificate
        except Exception as e:
            print('')
            print(e)
            print(certificate_id)
            print(ISCCCertificate.objects.filter(certificate_id=certificate_id, valid_from=valid_from))
    return None

def save_certificate_raw_materials(certificate, raw_materials):
    ISCCCertificateRawMaterial.objects.filter(certificate=certificate).delete()
    for raw_material in raw_materials.split(','):
        ISCCCertificateRawMaterial.objects.update_or_create(certificate=certificate, raw_material=raw_material.strip())

def save_certificate_scope(certificate, scopes):
    ISCCCertificateScope.objects.filter(certificate=certificate).delete()
    for scope in scopes.split(','):
        scope = scope.strip()
        if not scope:
            continue
        if scope not in VALID_SCOPES:
            if certificate.valid_until > today:
                print('Could not find scope [%s] in scopes' % (scope))
            continue
        ISCCCertificateScope.objects.update_or_create(certificate=certificate, scope=VALID_SCOPES[scope])
    
            
def load_certificates():
    filename = '%s/Certificates_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))
    csvfile = open(filename, 'r')
    reader = csv.DictReader(fix_nulls(csvfile), delimiter=',', quotechar='"')
    i = 0
    bulk_crt = []
    bulk_scopes = []
    bulk_rm = []
    for row in reader:
        i += 1
        # create certificate
        try:
            vf = row['valid_from'].split('.')
            valid_from = datetime.date(year=2000 + int(vf[2]), month=int(vf[1]), day=int(vf[0]))
        except:
            valid_from = datetime.date(year=1970, month=1, day=1)

        try:
            vu = row['valid_until'].split('.')
            valid_until = datetime.date(year=2000 + int(vu[2]), month=int(vu[1]), day=int(vu[0]))
        except:
            valid_from = datetime.date(year=1970, month=1, day=1)            
        d = {'addons': row['addons'],
             'issuing_cb': row['issuing_cb'],
             'location': row['map'],
        }
        # save certificate
        certificate = save_certificate(row['certificate'], row['certificate_holder'], valid_from, valid_until, d)
        if not certificate:
            continue
        # save associated scopes
        save_certificate_scope(certificate, row['scope'])
        # and raw materials
        save_certificate_raw_materials(certificate, row['raw_material'])
        print(i, end="\r")
    csvfile.close()
    return

        
def main():
    load_scopes()
    # load_raw_materials()
    load_certificates()
        
if __name__ == '__main__':
    main()
