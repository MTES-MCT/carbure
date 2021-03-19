import sys, os
import django
import csv
import calendar
import datetime
import re
import argparse
import openpyxl
import pandas as pd
from typing import TYPE_CHECKING, Dict, List, Optional
from pandas._typing import FilePathOrBuffer, Scalar

from django.core.mail import send_mail
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import REDCertScope, REDCertBiomassType, REDCertCertificate, REDCertCertificateScope, REDCertCertificateBioMass

today = datetime.date.today()
CSV_FOLDER = os.environ['CARBURE_HOME'] + '/web/fixtures/csv/'

def get_sheet_data(sheet, convert_float: bool) -> List[List[Scalar]]:
    data: List[List[Scalar]] = []
    for row in sheet.rows:
        data.append([convert_cell(cell, convert_float) for cell in row])
    return data


def convert_cell(cell, convert_float: bool) -> Scalar:
    from openpyxl.cell.cell import TYPE_BOOL, TYPE_ERROR, TYPE_NUMERIC

    if cell.is_date:
        return cell.value
    elif cell.data_type == TYPE_ERROR:
        return np.nan
    elif cell.data_type == TYPE_BOOL:
        return bool(cell.value)
    elif cell.value is None:
        return ""  # compat with xlrd
    elif cell.data_type == TYPE_NUMERIC:
        # GH5394
        if convert_float:
            val = int(cell.value)
            if val == cell.value:
                return val
        else:
            return float(cell.value)

    return cell.value


@transaction.atomic
def load_biomass_types(existing_biomass_types):
    new = []
    filename = '%s/redcert_biomass.csv' % (CSV_FOLDER)
    csvfile = open(filename, 'r')
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i += 1
        code = row['code']
        desc_fr = row['desc_fr']
        desc_en = row['desc_en']
        desc_de = row['desc_de']
        if code not in existing_biomass_types:
            new.append((code, desc_de))
        print('loading %s' % (code))
        try:
            o, c = REDCertBiomassType.objects.update_or_create(code=code, defaults={'description_fr': desc_fr, 'description_de': desc_de, 'description_en': desc_en})
        except:
            print('failed')
    return i, new

@transaction.atomic
def load_scopes(existing_scopes):
    new = []
    filename = '%s/redcert_scopes.csv' % (CSV_FOLDER)
    csvfile = open(filename, 'r')
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    i = 0
    for row in reader:
        i += 1
        scope = row['scope']
        desc_fr = row['desc_fr']
        desc_en = row['desc_en']
        desc_de = row['desc_de']
        if scope not in existing_scopes:
            new.append((scope, desc_de))
        print('loading %s' % (scope))
        try:
            o, c = REDCertScope.objects.update_or_create(scope=scope, defaults={'description_fr': desc_fr, 'description_de': desc_de, 'description_en': desc_en})
        except:
            print('failed')
    return i, new

def load_certificates(existing_certificates, scopes, biomass):
    new = []
    invalidated = []
    failed = []

    added_scopes = []
    removed_scopes = []
    added_biomass = []
    removed_biomass = []

    filename = '%s/REDcert-certificates.xlsx' % (CSV_FOLDER)
    wb = openpyxl.load_workbook(filename, data_only=True)
    sheet = wb.worksheets[0]
    data = get_sheet_data(sheet, convert_float=True)
    column_names = data[0]
    data = data[1:]
    df = pd.DataFrame(data, columns=column_names)
    df.fillna('', inplace=True)
    total_certs = len(df)    
    print(total_certs)
    i = 0
    transaction.set_autocommit(False)
    for row in df.iterrows():
        i += 1
        cert = row[1]
        #Identifier                            REDcert²-929-35291088
        #Name of the certificate holder               Quantafuel ASA
        #City                                                   Oslo
        #Post code                                               238
        #Country                                            Norwegen
        #Valid from                                       01.03.2021
        #Valid until                                      28.02.2022
        #Certified as                                        801,901
        #Certification body                       TÜV NORD CERT GmbH
        #Type                              Certificate REDcert² Chem
        #State                                                 Valid
        #Type of biomass  
        valid_from = datetime.datetime.strptime(cert['Valid from'], "%d.%m.%Y").date()
        valid_until = datetime.datetime.strptime(cert['Valid until'], "%d.%m.%Y").date()
        if cert.Identifier not in existing_certificates:
            new.append(cert)
        else:
            # existing certificate, check if valid_until has changed
            existingcert = existing_certificates[cert['Identifier']]
            if valid_until != existingcert.valid_until:
                invalidated.append((cert, existingcert))
        d = {'certificate_holder': cert['Name of the certificate holder'],
             'city': cert['City'],
             'zip_code': cert['Post code'],
             'country_raw': cert['Country'],
             'valid_from': valid_from,
             'valid_until': valid_until,
             'certificator': cert['Certification body'],
             'certificate_type': cert['Type'],
             'status': cert['State']
        }
        try:
            o, c = REDCertCertificate.objects.update_or_create(certificate_id=cert['Identifier'], defaults=d)
        except Exception as e:
            print('failed')
            print(e)
            failed.append(cert)
        # scopes
        existing_scopes = {s.scope.code: s for f in o.redcertcertificatescope_set.all()}
        cert_scopes = cert['Certified as'].split(',')
        for s in cert_scopes:
            s = s.trim()
            if s not in scopes:
                print('Could not find scope [%s] in REDCert scopes' % (s))
            else:
                s, c = REDCertCertificateScope.objects.update_or_create(certificate=o, scope=scopes[s])
                # did we already have it
                if scopes[s] in existing_scopes:
                    del existing_scopes[scopes[s]]
                else:
                    added_scopes.append((cert, scopes[s]))
        if len(existing_scopes) != 0:
            for es in existing_scopes.values():
                removed_scopes.append((cert, es))
                es.delete()

        # biomasses
        existing_biomasses = {s.biomass.code: s for f in o.redcertcertificatebiomass_set.all()}
        cert_biomass = cert['Type of biomass'].replace('/', ',').split()
        for b in cert_biomass:
            b = b.trim()
            if b not in biomass:
                print('Could not find scope [%s] in REDCert biomass' % (s))
            else:
                # did we already have it
                if biomass[b] in existing_biomasses:
                    del existing_biomasses[biomass[b]]
                else:
                    s, c = REDCertCertificateBioMass.objects.update_or_create(certificate=o, biomass=biomass[b])
                    added_biomass.append((cert, biomass[b]))
        if len(existing_biomasses) != 0:
            for es in existing_biomasses.values():
                removed_biomass.append((cert, es))
                es.delete()

        if i % 250 == 0:
            print(i)
            transaction.commit()
    transaction.commit()
    transaction.set_autocommit(True)
    return i, new, invalidated, failed, added_scopes, removed_scopes, added_biomass, removed_biomass

def summary(args, new_biomass, new_scopes, new_certificates, newly_invalidated_certificates, failed, nb_certificates):
    mail_content = "Hallo, <br />\n"
    mail_content += "Das Kärgement für zertificaten REDCert ist gut.<br />\n"
    mail_content += "%d zertificaten loaded<br />\n" % (nb_certificates)
    
    if len(new_biomass):
        for nb in new_biomass:
            mail_content += "Nouveau type de biomasse enregistré: %s - %s<br />\n" % (nb[0], nb[1])

    if len(new_scopes):
        for ns in new_scopes:
            mail_content += "Nouveau scope enregistré: %s - %s<br />\n" % (ns[0], ns[1])

    if len(new_certificates):
        for nc in new_certificates:
            mail_content += "Nouveau certificat enregistré<br />\n"
            mail_content += str(nc)
            mail_content += '<br />'

    if len(failed):
        for nc in failed:
            mail_content += "Impossible d'enregistrer le certificat suivante:<br />\n"
            mail_content += str(nc)
            mail_content += '<br />'

    fraud = False
    if len(newly_invalidated_certificates):
        fraud = True
        for (nic, previous) in newly_invalidated_certificates:
            mail_content += "**** ACHTUNG certificat invalidé *****<br />\n"
            mail_content += str(nic)
            mail_content += '<br />'
            mail_content += "Date de validité précédente: %s<br />" % (previous.valid_until)
            mail_content += str(previous.natural_key())
            mail_content += '<br />'


    subject = "Certificats REDCert"
    if fraud:
        subject += ' - ACHTUNG FRAUDE -'
    if args.email:
        dst = ['carbure@beta.gouv.fr']
        if args.test:
            dst = ['martin.planes@beta.gouv.fr']            
        send_mail(subject, mail_content, 'carbure@beta.gouv.fr', dst, fail_silently=False)
    else:
        print(mail_content)
        

def main(args):
    biomasses = {b.code: b for b in REDCertBiomassType.objects.all()}
    nb_biomass, new_biomass = load_biomass_types(biomasses)

    scopes = {s.scope: s for s in REDCertScope.objects.all()}
    nb_scopes, new_scopes = load_scopes(scopes)

    certificates = {c.certificate_id: c for c in REDCertCertificate.objects.prefetch_related('redcertcertificatescope_set', 'redcertcertificatebiomass_set').all()}
    nb_certificates, new_certificates, newly_invalidated_certificates, failed = load_certificates(certificates, scopes, biomasses)

    summary(args, new_biomass, new_scopes, new_certificates, newly_invalidated_certificates, failed, nb_certificates)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load REDCert certificates in database')
    parser.add_argument('--email', dest='email', action='store_true', default=False, help='Send a summary email')
    parser.add_argument('--test', dest='test', action='store_true', default=False, help='Send summary email to developers')    
    args = parser.parse_args()    
    main(args)
