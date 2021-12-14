import sys, os
import django
import csv
import calendar
import datetime
import re
import argparse
import unicodedata
from django.core.mail import send_mail

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GenericCertificate

VALID_SCOPES = {}
today = datetime.date.today()
CSV_FOLDER = '/tmp'

existing = {c.certificate_id: c for c in GenericCertificate.objects.filter(certificate_type=GenericCertificate.DBS)}

def load_certificates(valid=True):
    new = []
    invalidated = []
    if valid:
        filename = '%s/Certificates2BS_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))
    else:
        filename = '%s/Certificates2BS_invalid_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))        
    csvfile = open(filename, 'r')
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = 0
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
            
        d = {
            'certificate_type': GenericCertificate.DBS,
            'certificate_holder': unicodedata.normalize('NFKD', row['Nom']),
            'certificate_issuer': '',
            'address': unicodedata.normalize('NFKD', '%s - %s' % (row['Coordonnées'], row['Pays'])),
            'valid_from': valid_from,
            'valid_until': valid_until,
            'download_link': 'https://www.2bsvs.org/scripts/telecharger_certificat.php?certificat=%s' % (row['Numéro 2BS']),
            'scope': {'Type de certificate': row['Type de certification']},
            'input': None,
            'output': None,
        }
        if valid:
            d['scope']['valid'] = True
        else:
            d['scope']['valid'] = False
            if row['Numéro 2BS'] in existing:
                ec = existing[row['Numéro 2BS']]
                if 'valid' in ec.scope and ec.scope['valid'] is True:
                    invalidated.append(ec)
        try:
            o, c = GenericCertificate.objects.update_or_create(certificate_id=row['Numéro 2BS'], defaults=d)
            if c:
                new.append(o)
        except Exception as e:
            print('Could not load certificate')
            print(row)
            print(e)
        print(i, end="\r")
    csvfile.close()
    return i, new, invalidated

def summary(nb_valid, nb_invalid, new_valids, new_invalids, args):
    mail_content = "Güten Früden, <br />\n"
    mail_content += "Le chargement des certificats 2BS s'est bien passé.<br />\n"
    mail_content += "%d certificats valides et %d certificats invalides ont été chargés<br />\n" % (nb_valid, nb_invalid)
    
    if not len(new_valids):
        mail_content += "Aucun nouveau certificat détecté<br />\n"
    else:
        for nc in new_valids:
            mail_content += "Nouveau certificat 2BS détecté: [%s] - [%s]<br />\n" % (nc.certificate_id, nc.certificate_holder)

    if len(new_invalids):
        for nc in new_invalids:
            mail_content += "INVALIDATION. Certificat 2BS annulé ou périmé: [%s] - [%s]<br />\n" % (nc.certificate_id, nc.certificate_holder)
            
    if args.email:
        dst = ['carbure@beta.gouv.fr']
        if args.test:
            dst = ['martin.planes@beta.gouv.fr']            
        send_mail('Certificats 2BS', mail_content, 'carbure@beta.gouv.fr', dst, fail_silently=False)
    else:
        print(mail_content)
        

def main(args):
    # update data
    nb_valid_certificates, new_valids, _ = load_certificates(valid=True)
    nb_invalid_certificates, _, new_invalids = load_certificates(valid=False)
    summary(nb_valid_certificates, nb_invalid_certificates, new_valids, new_invalids, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load 2BS certificates in database')
    parser.add_argument('--email', dest='email', action='store_true', default=False, help='Send a summary email')
    parser.add_argument('--test', dest='test', action='store_true', default=False, help='Send summary email to developers')    
    args = parser.parse_args()    
    main(args)
