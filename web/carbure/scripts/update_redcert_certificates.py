import argparse
from collections import defaultdict
import datetime
import os
from typing import List, Tuple, cast

import django
import numpy as np
import openpyxl
import pandas as pd
import requests
from django.conf import settings
from django.core.mail import get_connection, send_mail
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet
from pandas._typing import Scalar

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GenericCertificate

today = datetime.date.today()
REDCERT_CERT_PAGE = "https://redcert.eu/ZertifikateDatenAnzeige.aspx"
REDCERT_EXPORT_URL = "https://redcert.eu/ExportZertifikate.aspx"
DESTINATION_FOLDER = "/tmp/"
REDCERT_ENGLISH_PARAMS = {"__EVENTTARGET": "ctl00$languageEnglishLinkButton"}

REDCERT_STATUS = {
    'valid certificate': GenericCertificate.VALID,
    'suspended certificate': GenericCertificate.SUSPENDED,
    'withdrawn certificate': GenericCertificate.WITHDRAWN,
    'terminated certificate': GenericCertificate.TERMINATED,
    'expired certificate': GenericCertificate.EXPIRED
}

def update_redcert_certificates(email: bool = False, test: bool = False) -> None:
    download_redcert_certificates()
    nb_certificates, new_certificates, newly_invalidated_certificates = save_redcert_certificates()
    send_email_summary(nb_certificates, new_certificates, newly_invalidated_certificates, email)

def download_redcert_certificates() -> None:
    session = requests.Session()
    # first, load the page showing the list of redcert certs -> it sets a session cookie
    print("Initializing connection to redcert servers...")
    session.get(REDCERT_CERT_PAGE)
    session.post(REDCERT_CERT_PAGE, data=REDCERT_ENGLISH_PARAMS)  # switch to english
    # now we can try to download the actual xlsx file
    print("Downloading the list of certificates...")
    res = session.get(REDCERT_EXPORT_URL, allow_redirects=True)
    filename = "%s/REDcert-certificates.xlsx" % (DESTINATION_FOLDER)
    open(filename, "wb").write(res.content)
    print("File was created successfully.")

def save_redcert_certificates() -> Tuple[int, list, list]:
    certificates_by_status = defaultdict(list)
    invalidated = []

    existing = GenericCertificate.objects.filter(certificate_type=GenericCertificate.REDCERT)
    existing_by_id = {c.certificate_id: c for c in existing}

    filename = "%s/REDcert-certificates.xlsx" % (DESTINATION_FOLDER)
    df = pd.read_excel(filename)
    df.fillna("", inplace=True)
    i = 0
    for row in df.iterrows():
        i += 1
        cert = row[1]
        # Identifier                            REDcert²-929-35291088
        # Name of the certificate holder               Quantafuel ASA
        # City                                                   Oslo
        # Post code                                               238
        # Country                                            Norwegen
        # Valid from                                       01.03.2021
        # Valid until                                      28.02.2022
        # Certified as                                        801,901
        # Certification body                       TÜV NORD CERT GmbH
        # Type                              Certificate REDcert² Chem
        # State                                     valid certificate
        # Type of biomass

        certificate_id = cert["Identifier"]
        existing_cert = existing_by_id.get(certificate_id)
        status = REDCERT_STATUS.get(cert["State"])
        valid_from = datetime.datetime.strptime(cert["Valid from"], "%d.%m.%Y").date()
        valid_until = datetime.datetime.strptime(cert["Valid until"], "%d.%m.%Y").date()
       
        if existing_cert.status == GenericCertificate.VALID and status != GenericCertificate.VALID:
            invalidated.append(existing_cert)

        certificates_by_status[status].append({
                "certificate_id": certificate_id,
                "certificate_type": GenericCertificate.REDCERT,
                "certificate_holder": cert["Name of the certificate holder"],
                "certificate_issuer": cert["Certification body"],
                "address": "%s, %s, %s" % (cert["City"], cert["Post code"], cert["Country"]),
                "valid_from": valid_from,
                "valid_until": valid_until,
                "scope": "%s" % (cert["Type"]),
                "input": {"Type of biomass": cert["Type of biomass"]},
                "output": None,
                "status": status
            })
    
    existing = []
    new = []

    for status, certificates in certificates_by_status.items():
        existing_for_status, new_for_status = GenericCertificate.bulk_create_or_update(certificates, status)
        existing += existing_for_status
        new += new_for_status

    print("[REDcert Certificates] %d updated, %d created" % (len(existing), len(new)))
    return i, new, invalidated


def send_email_summary(
    nb_certificates: int,
    new_certificates: list,
    newly_invalidated_certificates: list,
    email: bool,
) -> None:
    mail_content = "Bonjour, <br />\n"
    mail_content += "La mise à jour des certificats REDcert s'est bien passée.<br />\n"
    mail_content += "%d certificats vérifiés<br />\n" % (nb_certificates)

    if len(new_certificates):
        mail_content += "%d nouveaux certificats enregistrés :<br />\n" % len(new_certificates)
        for nc in new_certificates:
            mail_content += "%s - %s" % (nc.certificate_id, nc.certificate_holder)
            mail_content += "<br />"

    if len(newly_invalidated_certificates):
        for cert in newly_invalidated_certificates:
            mail_content += "**** Certificat %s *****<br />" % (cert.status)
            mail_content += "%s - %s" % (cert.certificate_id, cert.certificate_holder)
            mail_content += "<br />"
            mail_content += "Date de fin: %s<br />" % (cert.valid_until)

    try:
        connection = get_connection()
        connection.open()
        if email:
            send_mail(
                "Certificats REDcert",
                mail_content,
                settings.DEFAULT_FROM_EMAIL,
                ["carbure@beta.gouv.fr"],
                fail_silently=False,
                connection=connection,
            )
        else:
            print(mail_content)
        connection.close()
    except Exception:
        print("Error: Could not open connection to email backend")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load REDCert certificates in database")
    parser.add_argument("--email", dest="email", action="store_true", default=False, help="Send a summary email")
    parser.add_argument("--test", dest="test", action="store_true", default=False, help="Send email to developers")
    args = parser.parse_args()
    update_redcert_certificates(args.email, args.test)
