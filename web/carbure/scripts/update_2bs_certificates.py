#!/usr/bin/env python
# coding: utf-8

import argparse
from typing import Tuple
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import os
import django
import csv
import argparse
import unicodedata
from django.conf import settings
from django.core.mail import send_mail, get_connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.utils import bulk_update_or_create
from core.models import GenericCertificate


DESTINATION_FOLDER = "/tmp"

DBS_VALID_URL = "https://www.2bsvs.org/cert_valides.html"
DBS_INVALID_URL = "https://www.2bsvs.org/cert_retires.html"

DBS_NUMBER_KEY = "Numéro de Certificat 2BS"
DBS_COMPANY_NAME_KEY = "Nom de l’opérateur économique"
DBS_ADDRESS_KEY = "Adresse"
DBS_COUNTRY_KEY = "Pays"


def update_2bs_certificates(email: bool = False) -> None:
    # download certificates from 2bs website
    download_certificates(DBS_VALID_URL)
    download_certificates(DBS_INVALID_URL, valid=False)
    # save certificates to database
    nb_valid_certificates, new_valids = save_2bs_certificates(valid=True)
    nb_invalid_certificates, new_invalids = save_2bs_certificates(valid=False)
    # send email summary
    send_email_summary(nb_valid_certificates, nb_invalid_certificates, new_valids, new_invalids, email)


def download_certificates(url: str, valid: bool = True) -> None:
    html_content = requests.get(url).text.replace("<br/>", " ").replace("<br />", " ")
    soup = BeautifulSoup(html_content, "lxml")
    table = soup.find_all("table")
    df = pd.read_html(str(table))[0]
    df = df[~df[DBS_NUMBER_KEY].isnull()]  # Pour une raison inconnue, la ligne de coordonnées est dupliquée
    if valid:
        pd.DataFrame.to_csv(df, "%s/Certificates2BS_%s.csv" % (DESTINATION_FOLDER, str(date.today())), index=False)
    else:
        pd.DataFrame.to_csv(
            df, "%s/Certificates2BS_invalid_%s.csv" % (DESTINATION_FOLDER, str(date.today())), index=False
        )


def save_2bs_certificates(valid: bool = True) -> Tuple[int, list]:
    today = date.today()
    certificates = []
    if valid:
        filename = "%s/Certificates2BS_%s.csv" % (DESTINATION_FOLDER, today.strftime("%Y-%m-%d"))
    else:
        filename = "%s/Certificates2BS_invalid_%s.csv" % (DESTINATION_FOLDER, today.strftime("%Y-%m-%d"))
    csvfile = open(filename, "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar='"')
    i = 0
    for row in reader:
        i += 1
        # valid: Nom,Coordonnées,Pays,Type de certification,Numéro de Certificat 2BS,Date originale de certification,Date de fin de validité du certificat,Certificat
        # create certificate
        try:
            vf = row["Date originale de certification"].split("/")
            valid_from = date(year=int(vf[2]), month=int(vf[1]), day=int(vf[0]))
        except:
            valid_from = date(year=1970, month=1, day=1)

        try:
            vu = row["Date de fin de validité du certificat"].split("/")
            valid_until = date(year=int(vu[2]), month=int(vu[1]), day=int(vu[0]))
        except:
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
                "scope": "%s" % (row["Type de certification"]),
                "input": None,
                "output": None,
            }
        )
    existing, new = bulk_update_or_create(GenericCertificate, "certificate_id", certificates)
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
