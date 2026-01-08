#!/usr/bin/env python
# coding: utf-8

import argparse
import csv
import os
import unicodedata
from datetime import date
from typing import Tuple
from io import StringIO

import django
import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import get_connection, send_mail

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import GenericCertificate  # noqa: E402
from core.utils import bulk_update_or_create  # noqa: E402

DESTINATION_FOLDER = "/tmp"

DBS_URL = "https://www.2bsvs.org/fr/certificats-bloc-parent"

DBS_NUMBER_KEY = "Numéro de Certificat 2BS"
DBS_COMPANY_NAME_KEY = "Nom de l’opérateur économique"
DBS_ADDRESS_KEY = "Adresse"
DBS_COUNTRY_KEY = "Pays"
DBS_VALID_FROM_KEY = "Date de début de validité du certificat"
DBS_VALID_UNTIL_KEY = "Date de fin de validité du certificat"
DBS_WITHDRAWAL_DATE_KEY = "Date de retrait du certificat"
DBS_SUSPENSION_DATE_KEY = "Date de suspension du certificat"
DBS_TYPE_KEY = "Type d'activité"

DBS_STATUS = {
    GenericCertificate.VALID: f"{DBS_URL}/certificats-valides/",
    GenericCertificate.WITHDRAWN: f"{DBS_URL}/certificats-retires/",
    GenericCertificate.SUSPENDED: f"{DBS_URL}/certificats-suspendus/",
    GenericCertificate.TERMINATED: f"{DBS_URL}/certificats-resilies/",
}

def update_2bs_certificates(email: bool = False) -> None:
    nb_valid_certificates = 0
    nb_invalid_certificates = 0
    new_valids = []
    new_invalids = []

    for status, url in DBS_STATUS.items():
        download_certificates(url, status)
        count, new = save_2bs_certificates(status)
        if status == GenericCertificate.VALID:
            nb_valid_certificates += count
            new_valids += new
        else:
            nb_invalid_certificates += count
            new_invalids += new

    # send email summary
    send_email_summary(nb_valid_certificates, nb_invalid_certificates, new_valids, new_invalids, email)


def download_certificates(url: str, status: str) -> None:
    html_content = requests.get(url).text.replace("<br/>", " ").replace("<br />", " ")
    soup = BeautifulSoup(html_content, "lxml")
    table = soup.find_all("table")
    html_io = StringIO(str(table))
    df = pd.read_html(html_io)[0]
    df = df[~df[DBS_NUMBER_KEY].isnull()]  # Pour une raison inconnue, la ligne de coordonnées est dupliquée
    pd.DataFrame.to_csv(df, "%s/Certificates2BS_%s_%s.csv" % (DESTINATION_FOLDER, status.lower(), str(date.today())), index=False)


def save_2bs_certificates(status: str) -> Tuple[int, list]:
    today = date.today()
    certificates = []
    filename = "%s/Certificates2BS_%s_%s.csv" % (DESTINATION_FOLDER, status, today.strftime("%Y-%m-%d"))
    csvfile = open(filename, "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
    i = 0
    for row in reader:
        i += 1
        # valid: Nom,Coordonnées,Pays,Type de certification,Numéro de Certificat 2BS,Date de début de validité du certificat,Date de fin de validité du certificat,Certificat  # noqa: E501
        # create certificate
        try:
            vf = row[DBS_VALID_FROM_KEY].split("/")
            valid_from = date(year=int(vf[2]), month=int(vf[1]), day=int(vf[0]))
        except Exception:
            valid_from = date(year=1970, month=1, day=1)

        try:
            if status in [GenericCertificate.VALID, GenericCertificate.TERMINATED]:
                vu = row[DBS_VALID_UNTIL_KEY].split("/")
                valid_until = date(year=int(vu[2]), month=int(vu[1]), day=int(vu[0]))
            elif status == GenericCertificate.WITHDRAWN:
                vu = row[DBS_WITHDRAWAL_DATE_KEY].split("/")
                valid_until = date(year=int(vu[2]), month=int(vu[1]), day=int(vu[0]))
            elif status == GenericCertificate.SUSPENDED:
                vu = row[DBS_SUSPENSION_DATE_KEY].split("/")
                valid_until = date(year=int(vu[2]), month=int(vu[1]), day=int(vu[0]))
        except Exception:
            valid_until = date(year=1970, month=1, day=1)

        

        certificates.append(
            {
                "certificate_id": row[DBS_NUMBER_KEY],
                "certificate_type": GenericCertificate.DBS,
                "certificate_holder": unicodedata.normalize("NFKD", row[DBS_COMPANY_NAME_KEY]),
                "certificate_issuer": "",
                "address": unicodedata.normalize("NFKD", "%s - %s" % (row[DBS_ADDRESS_KEY], row[DBS_COUNTRY_KEY])),
                "valid_from": valid_from,
                "valid_until": valid_until,
                "download_link": "https://www.2bsvs.org/scripts/telecharger_certificat.php?certificat=%s"
                % (row[DBS_NUMBER_KEY]),
                "scope": "%s" % (row[DBS_TYPE_KEY]),
                "input": None,
                "output": None,
                "status": status
            }
        )

    existing, new = GenericCertificate.bulk_create_or_update(certificates, status)
    
    print("[2BS Certificates] %d updated, %d created" % (len(existing), len(new)))
    csvfile.close()
    return i, new


def send_email_summary(
    nb_valid: int,
    nb_invalid: int,
    new_valids: list,
    new_invalids: list,
    email: bool = False,
) -> None:
    mail_content = "Güten Früden,<br />\n"
    mail_content += "La mise à jour des certificats 2BS s'est bien passée.<br />\n"
    mail_content += "%d certificats valides et %d certificats expirés ont été chargés<br />\n" % (
        nb_valid,
        nb_invalid,
    )

    if not len(new_valids):
        mail_content += "Aucun nouveau certificat détecté<br />\n"
    else:
        for nc in new_valids:
            mail_content += "Nouveau certificat 2BS détecté: [%s] - [%s]<br />\n" % (
                nc.certificate_id,
                nc.certificate_holder,
            )

    if len(new_invalids):
        for nc in new_invalids:
            mail_content += "INVALIDATION. Certificat 2BS annulé ou périmé: [%s] - [%s]<br />\n" % (
                nc.certificate_id,
                nc.certificate_holder,
            )

    if email:
        try:
            connection = get_connection()
            connection.open()
            send_mail(
                "Certificats 2BS",
                mail_content,
                settings.DEFAULT_FROM_EMAIL,
                ["carbure@beta.gouv.fr"],
                fail_silently=False,
                connection=connection,
            )
            connection.close()
        except Exception:
            print("Error: Could not open connection to email backend")
            return
    else:
        print(mail_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load 2BS certificates in database")
    parser.add_argument("--email", dest="email", action="store_true", default=False, help="Send a summary email")
    parser.add_argument("--test", dest="test", action="store_true", default=False, help="Send email to developers")
    args = parser.parse_args()
    update_2bs_certificates(args.email)
