import sys, os
import django
import csv
import calendar
import datetime
import argparse
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GenericCertificate

VALID_SCOPES = {}
today = datetime.date.today()
CSV_FOLDER = '/tmp'

def fix_nulls(s):
    for line in s:
        yield line.replace('\0', ' ')

def load_certificates():
    new = []
    filename = '%s/Certificates_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))
    df = pd.read_csv(filename, sep=',', quotechar='"', lineterminator="\n")
    df.fillna('', inplace=True)
    for i, row in df.iterrows():
        try:
            if '.' in row['valid_from']:
                vf = row['valid_from'].split('.')
            elif '-' in row['valid_from']:
                valid_from = datetime.datetime.strptime(row['valid_from'], '%Y-%m-%d').date()
            else:
                print("Unrecognized date format [%s]" % (row['valid_from']))
                print(row)
                valid_from = datetime.date(year=1970, month=1, day=1)
        except:
            valid_from = datetime.date(year=1970, month=1, day=1)

        try:
            if '.' in row['valid_until']:
                vu = row['valid_until'].split('.')
                valid_until = datetime.date(year=2000 + int(vu[2]), month=int(vu[1]), day=int(vu[0]))
            elif '-' in row['valid_until']:
                valid_until = datetime.datetime.strptime(row['valid_until'], '%Y-%m-%d').date()
            else:
                print("Unrecognized date format [%s]" % (row['valid_until']))
                print(row)
                valid_until = datetime.date(year=1970, month=1, day=1)
        except:
            valid_until = datetime.date(year=1970, month=1, day=1)

        if ',' in row['certificate_holder']:
            holder = row['certificate_holder'].split(',')[0]
        else:
            holder = row['certificate_holder']
        d = {
            'certificate_type': GenericCertificate.ISCC,
            'certificate_holder': holder,
            'certificate_issuer': row['issuing_cb'],
            'address': row['certificate_holder'],
            'valid_from': valid_from,
            'valid_until': valid_until,
            'scope': "%s" % (row['scope']),
            'download_link': row['certificate_report'],
            'input': {'raw_material': row['raw_material']},
            'output': '',
        }
        try:
            print('Saving %s' % (row['certificate']))
            o, c = GenericCertificate.objects.update_or_create(certificate_id=row['certificate'], defaults=d)
            if c:
                new.append(c)
        except Exception as e:
            print('could not create certificate:')
            print(row)
            print(e)
    return i, new


def summary(nb, new, args):
    mail_content = "Güten Früden, <br />\n"
    mail_content += "Le chargement des certificats ISCC s'est bien passé.<br />\n"
    mail_content += "%d certificats ont été chargés<br />\n" % (nb)

    if not len(new):
        mail_content += "Aucun nouveau certificat détecté<br />\n"
    else:
        for nc in new:
            mail_content += "Nouveau certificat ISCC détecté: [%s] - [%s]<br />\n" % (nc.certificate_id, nc.certificate_holder)

    if args.email:
        dst = ['carbure@beta.gouv.fr']
        send_mail('Certificats ISCC - %d certificats - %d nouveaux' % (nb, len(new)), mail_content, settings.DEFAULT_FROM_EMAIL, dst, fail_silently=False)
    else:
        print(mail_content)


def main(args):
    load_certificates()
    nb_certificates, new_certificates = load_certificates()
    summary(nb_certificates, new_certificates, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load ISCC certificates in database')
    parser.add_argument('--email', dest='email', action='store_true', default=False, help='Send a summary email')
    parser.add_argument('--test', dest='test', action='store_true', default=False, help='Send summary email to developers only')
    args = parser.parse_args()
    main(args)

