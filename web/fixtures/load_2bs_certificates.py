import sys, os
import django
import csv
import calendar
import datetime
import re
import argparse
from django.core.mail import send_mail

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
        existing_scopes = {cs.scope: cs for cs in DBSCertificateScope.objects.filter(certificate=certificate)}
        for s in scopes:
            dbscope = scope2dbscope[s]
            if dbscope in existing_scopes:
                del existing_scopes[dbscope]
            else:
                DBSCertificateScope.objects.update_or_create(certificate=certificate, scope=scope2dbscope[s])
        if len(existing_scopes):
            print('The following scopes have been removed from certificate [%s] - [%s]' % (certificate.certificate_id, certificate.certificate_holder))
            for k, v in existing_scopes.items():
                print(v.scope.certification_type)
                v.delete()
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
             'certification_type': '',
             'download_link': 'https://www.2bsvs.org/scripts/telecharger_certificat.php?certificat=%s' % (row['Numéro 2BS'])}
        # save certificate
        certificate = save_certificate(row['Numéro 2BS'], [], d)
        if not certificate:
            continue
        print(i, end="\r")
    print('')
    csvfile.close()
    return i

def load_valid_certificates():
    filename = '%s/Certificates2BS_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))
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
        d = {'certificate_holder': row['Nom'],
             'holder_address': '%s - %s' % (row['Coordonnées'], row['Pays']),
             'valid_from': valid_from,
             'valid_until': valid_until,
             'download_link': 'https://www.2bsvs.org/scripts/telecharger_certificat.php?certificat=%s' % (row['Numéro 2BS']),
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
    print('')
    csvfile.close()
    return i

def summary(nb_valid, nb_invalid, new_scopes, new_certificates, new_certificates_scopes, args):
    mail_content = "Güten Früden, <br />\n"
    mail_content += "Le chargement des certificats 2BS s'est bien passé.<br />\n"

    mail_content += "%d certificats valides et %d certificats invalides ont été chargés<br />\n" % (nb_valid, nb_invalid)
    
    if not len(new_scopes):
        mail_content += "Aucun nouveau type de certification détecté<br />\n"
    else:
        for ns in new_scopes:
            mail_content += "Nouveau type de certification 2BS détecté: %s<br />\n" % (ns.certification_type)

    if not len(new_certificates):
        mail_content += "Aucun nouveau certificat détecté<br />\n"
    else:
        for nc in new_certificates:
            mail_content += "Nouveau certificat 2BS détecté: [%s] - [%s]<br />\n" % (nc.certificate_id, nc.certificate_holder)

    if not len(new_certificates_scopes):
        mail_content += "Aucune modification de certificat détectée<br />\n"
    else:
        for ncs in new_certificates_scopes:
            mail_content += "Mise à jour du certificat [%s] - [%s]: Ajout de la certification: %s<br />\n" % (ncs.certificate.certificate_id, ncs.certificate.certificate_holder, ncs.scope.certification_type)
    if args.email:
        dst = ['carbure@beta.gouv.fr']
        if args.test:
            dst = ['martin.planes@beta.gouv.fr']            
        send_mail('Certificats 2BS', mail_content, 'carbure@beta.gouv.fr', dst, fail_silently=False)
    else:
        print(mail_content)
        

def main(args):
    # get latest data from db
    try:
        last_scope_id = DBSScope.objects.latest('id').id
        last_certificate_id = DBSCertificate.objects.latest('id').id
        last_certificate_scope_id = DBSCertificateScope.objects.latest('id').id
    except:
        last_scope_id = 0
        last_certificate_id = 0
        last_certificate_scope_id = 0
        
    # update data
    nb_valid_certificates = load_valid_certificates()
    print('')
    nb_invalid_certificates = load_invalid_certificates()
        
    # check what has been updated
    new_scopes = []
    new_certificates = []
    new_certificates_scopes = []
    if last_scope_id != DBSScope.objects.latest('id').id:
        new_scopes = DBSScope.objects.filter(id__gt=last_scope_id)
    if last_certificate_id != DBSCertificate.objects.latest('id').id:
        new_certificates = DBSCertificate.objects.filter(id__gt=last_certificate_id)
    if last_certificate_scope_id != DBSCertificateScope.objects.latest('id').id:
        new_certificates_scopes = DBSCertificateScope.objects.filter(id__gt=last_certificate_scope_id)
    summary(nb_valid_certificates, nb_invalid_certificates, new_scopes, new_certificates, new_certificates_scopes, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load 2BS certificates in database')
    parser.add_argument('--email', dest='email', action='store_true', default=False, help='Send a summary email')
    parser.add_argument('--test', dest='test', action='store_true', default=False, help='Send summary email to developers')    
    args = parser.parse_args()    
    main(args)
