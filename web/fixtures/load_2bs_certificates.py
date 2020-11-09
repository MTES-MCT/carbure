import sys, os
import django
import csv
import calendar
import datetime
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import DBSCertificate, DBSScope, DBSCertificateScope

VALID_SCOPES = {}
today = datetime.date.today()
CSV_FOLDER = '/tmp'

def save_certificate(certificate_id, scopes, details):
    scope2dbscope = {}
    for s in scopes:
        scope, created = DBSScope.objects.update_or_create(certification_type=s)
        scope2dbscope[s] = scope
    try:
        certificate, created = DBSCertificate.objects.update_or_create(certificate_id=certificate_id, defaults=details)
        DBSCertificateScope.objects.filter(certificate=certificate).delete()
        for s in scopes:
            DBSCertificateScope.objects.update_or_create(certificate=certificate, scope=scope2dbscope[s])
        return certificate
    except Exception as e:
        print('')
        print(e)
        print(certificate_id)
    return None

def load_invalid_certificates():
    filename = '%s/Certificates2BS_invalid_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))
    csvfile = open(filename, 'r')
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = 0
    bulk_crt = []
    for row in reader:
        i += 1
        # invalid: Nom,Coordonnées,Numéro 2BS,Date de retrait
        # create certificate
        try:
            vu = row['Date de retrait'].split('/')
            valid_until = datetime.date(year=int(vu[0]), month=int(vu[1]), day=int(vu[2]))
        except:
            valid_until = datetime.date(year=1970, month=1, day=1)            
        d = {'certificate_holder': row['Nom'],
             'holder_address': '%s' % (row['Coordonnées']),
             'valid_from': datetime.date(year=1970, month=1, day=1),
             'valid_until': valid_until,
             'certification_type': ''}
        # save certificate
        certificate = save_certificate(row['Numéro 2BS'], [], d)
        if not certificate:
            continue
        print(i, end="\r")
    csvfile.close()
    return

def load_valid_certificates():
    filename = '%s/Certificates2BS_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))
    csvfile = open(filename, 'r')
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = 0
    bulk_crt = []
    for row in reader:
        i += 1
        # valid: Nom,Coordonnées,Pays,Type de certification,Numéro 2BS,Date originale de certification,Date de fin de validité du certificat,Certificat
        # create certificate
        try:
            vf = row['Date originale de certification'].split('/')
            valid_from = datetime.date(year=int(vf[2]), month=int(vf[1]), day=int(vf[0]))
        except:
            valid_from = datetime.date(year=1970, month=1, day=1)

        try:
            vu = row['Date de fin de validité du certificat'].split('/')
            valid_until = datetime.date(year=int(vu[2]), month=int(vu[1]), day=int(vu[0]))
        except:
            valid_until = datetime.date(year=1970, month=1, day=1)            
        d = {'certificate_holder': row['Nom'],
             'holder_address': '%s - %s' % (row['Coordonnées'], row['Pays']),
             'valid_from': valid_from,
             'valid_until': valid_until,
            }
        scopes = []
        if row['Type de certification']:
            pattern = r"([^(,]*(?:\([^)]*\))?),?"
            scopes = re.split(pattern, row['Type de certification'])
            scopes = [s.strip() for s in scopes if s]
        # save certificate
        certificate = save_certificate(row['Numéro 2BS'], scopes, d)
        if not certificate:
            continue
        print(i, end="\r")
    csvfile.close()
    return

        
def main():
    load_valid_certificates()
    print('')
    load_invalid_certificates()
        
if __name__ == '__main__':
    main()
