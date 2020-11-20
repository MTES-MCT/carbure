import sys, os
import django
import csv
import calendar
import datetime
import argparse
from django.core.mail import send_mail

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
    deletions = []
    existing_scopes = {cs.scope.scope: cs for cs in ISCCCertificateScope.objects.filter(certificate=certificate)}
    for scope in scopes.split(','):
        scope = scope.strip()
        if not scope:
            continue
        if scope not in VALID_SCOPES:
            if certificate.valid_until > today:
                print('Could not find scope [%s] in scopes' % (scope))
            continue
        if scope in existing_scopes:
            del existing_scopes[scope]
        else:
            ISCCCertificateScope.objects.update_or_create(certificate=certificate, scope=VALID_SCOPES[scope])
    if len(existing_scopes):
        for k, v in existing_scopes.items():
            v.delete()
            deletions.append(v)
    return deletions

def load_certificates():
    nb_valid = 0
    nb_expired = 0
    certificate_deletions = []
    certificate_scopes_deletions = []
    filename = '%s/Certificates_%s.csv' % (CSV_FOLDER, today.strftime('%Y-%m-%d'))
    csvfile = open(filename, 'r')
    reader = csv.DictReader(fix_nulls(csvfile), delimiter=',', quotechar='"')
    i = 0
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
            valid_until = datetime.date(year=1970, month=1, day=1)            
        d = {'addons': row['addons'],
             'issuing_cb': row['issuing_cb'],
             'location': row['map'],
             'download_link': row['certificate_report'],
        }
        # save certificate
        certificate = save_certificate(row['certificate'], row['certificate_holder'], valid_from, valid_until, d)
        if not certificate:
            continue
        # save associated scopes
        certificate_scopes_deletions += save_certificate_scope(certificate, row['scope'])
        # and raw materials
        save_certificate_raw_materials(certificate, row['raw_material'])
        print(i, end="\r")
        if valid_until >= today:
            nb_valid += 1
        else:
            nb_expired += 1
    csvfile.close()
    return nb_valid, nb_expired, certificate_scopes_deletions


def summary(nb_valid, nb_invalid, new_scopes, new_certificates, new_certificates_scopes, scope_deletions, args):
    mail_content = "Güten Früden, <br />\n"
    mail_content += "Le chargement des certificats ISCC s'est bien passé.<br />\n"

    mail_content += "%d certificats valides et %d certificats expirés ont été chargés<br />\n" % (nb_valid, nb_invalid)
    
    if not len(new_scopes):
        mail_content += "Aucun nouveau type de certification détecté<br />\n"
    else:
        for ns in new_scopes:
            mail_content += "Nouveau type de certification ISCC détecté: %s - %s<br />\n" % (ns.scope, ns.description)

    if not len(new_certificates):
        mail_content += "Aucun nouveau certificat détecté<br />\n"
    else:
        for nc in new_certificates:
            mail_content += "Nouveau certificat ISCC détecté: [%s] - [%s]<br />\n" % (nc.certificate_id, nc.certificate_holder)

    if not len(new_certificates_scopes):
        mail_content += "Aucune modification de certificat détectée<br />\n"
    else:
        for ncs in new_certificates_scopes:
            mail_content += "Mise à jour du certificat [%s] - [%s]: Ajout de la certification: %s - %s<br />\n" % (ncs.certificate.certificate_id, ncs.certificate.certificate_holder, ncs.scope.scope, ncs.scope.description)

    if len(scope_deletions):
        for sd in scope_deletions:
            mail_content += "Suppression du scope [%s] - [%s] pour le certificat [%s] - [%s]" % (sd.scope.scope, sd.scope.description, sd.certificate.certificate_id, sd.certificate.certificate_holder)

    if args.email:
        if args.test:
            dst = ['martin.planes@beta.gouv.fr']
        else:
            dst = ['carbure@beta.gouv.fr']
        send_mail('Certificats ISCC - %d certificats - %d nouveaux' % (nb_valid + nb_invalid, len(new_certificates)), mail_content, 'carbure@beta.gouv.fr', dst, fail_silently=False)
    else:
        print(mail_content)
        
        
def main(args):
    load_scopes()
    load_certificates()
        
    # get latest data from db
    try:
        last_scope_id = ISCCScope.objects.latest('id').id
        last_certificate_id = ISCCCertificate.objects.latest('id').id
        last_certificate_scope_id = ISCCCertificateScope.objects.latest('id').id
    except:
        last_scope_id = 0
        last_certificate_id = 0
        last_certificate_scope_id = 0
        
    # update data
    nb_valid_certificates, nb_expired_certificates, scope_deletions = load_certificates()
        
    # check what has been updated
    new_scopes = []
    new_certificates = []
    new_certificates_scopes = []
    if last_scope_id != ISCCScope.objects.latest('id').id:
        new_scopes = ISCCScope.objects.filter(id__gt=last_scope_id)
    if last_certificate_id != ISCCCertificate.objects.latest('id').id:
        new_certificates = ISCCCertificate.objects.filter(id__gt=last_certificate_id)
    if last_certificate_scope_id != ISCCCertificateScope.objects.latest('id').id:
        new_certificates_scopes = ISCCCertificateScope.objects.filter(id__gt=last_certificate_scope_id)
    summary(nb_valid_certificates, nb_expired_certificates, new_scopes, new_certificates, new_certificates_scopes, scope_deletions, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load ISCC certificates in database')
    parser.add_argument('--email', dest='email', action='store_true', default=False, help='Send a summary email')
    parser.add_argument('--test', dest='test', action='store_true', default=False, help='Send summary email to developers only')    
    args = parser.parse_args()    
    main(args)

