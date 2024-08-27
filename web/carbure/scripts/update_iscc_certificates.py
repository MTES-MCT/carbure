#!/usr/bin/env python
# coding: utf-8

# Extraction des certificats ISCC https://www.iscc-system.org/certificates/all-certificates/
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

import argparse
import json
import re
import shutil
from datetime import date, datetime  # Pour le nom du fichier sauvegardé
from os import listdir
from os.path import isfile
from typing import Tuple, cast

import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import get_connection, send_mail

from core.models import GenericCertificate
from core.utils import bulk_update_or_create

ISCC_DATA_URL = "https://www.iscc-system.org/wp-admin/admin-ajax.php?action=get_wdtable&table_id=2"
ISCC_CERT_PAGE = "https://www.iscc-system.org/certificates/all-certificates/"
DESTINATION_FOLDER = "/tmp"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}
PAGELENGTH = 3000


# Download ISCC certificates and save them to the database
def update_iscc_certificates(email: bool = False, test: bool = False, latest: bool = False, batch: int = 1000) -> None:
    download_iscc_certificates(test, latest)
    i, new = save_iscc_certificates(email, batch)
    send_email_summary(i, new, email)


def download_iscc_certificates(test: bool, latest: bool) -> None:
    # On récupère le wdtNonce du jour
    nonce, soup = get_wdtNonce()

    # Nombre de requêtes
    r = requests.post(ISCC_DATA_URL, data={"length": 1, "start": 0, "draw": 1, "wdtNonce": nonce}, headers=HEADERS)
    recordsTotal = 3 if test else int(json.loads(r.content.decode("utf-8"))["recordsTotal"])
    print(f"> Found {recordsTotal} ISCC certificates")

    # Récupération du contenu
    data = fetch_certificate_data(nonce, recordsTotal, test, latest)

    # On retire les balises html pour ne garder que le contenu
    cleaned_data = clean_certificate_data(data, soup)

    # Sauvegarde
    filename = "%s/Certificates_%s.csv" % (DESTINATION_FOLDER, str(date.today()))
    pd.DataFrame.to_csv(cleaned_data, filename, index=False)

    ## Comparaison pour extraire les doublons
    # 1) Création d'un historique
    files = [f for f in listdir(DESTINATION_FOLDER) if isfile("%s/%s" % (DESTINATION_FOLDER, f))]
    files.sort()
    certificatesFiles = [f for f in files if re.match("Certificates_[0-9]{4}-[0-9]{2}-[0-9]{2}.csv", f)]
    histoFiles = [f for f in files if re.match("History_[0-9]{4}-[0-9]{2}-[0-9]{2}.csv", f)]

    # Il n'y a pas d'historique --> le fichier crée est celui du jour. Il y a maintenant un historique
    if len(histoFiles) == 0:
        histoFile = re.sub("Certificates", "History", certificatesFiles[-1])
        shutil.copy("%s/%s" % (DESTINATION_FOLDER, certificatesFiles[-1]), "%s/%s" % (DESTINATION_FOLDER, histoFile))

    # 2) Ouverture et concaténation
    files = [f for f in listdir(DESTINATION_FOLDER) if isfile("%s/%s" % (DESTINATION_FOLDER, f))]
    files.sort()
    histoFiles = [f for f in files if re.match("History_[0-9]{4}-[0-9]{2}-[0-9]{2}.csv", f)]
    histo = pd.read_csv(f"{DESTINATION_FOLDER}/{histoFiles[-1]}", sep=",", quotechar='"', lineterminator="\n")
    histo["date"] = str(re.sub("History_([0-9]{4}-[0-9]{2}-[0-9]{2}).csv", "\\1", histoFiles[-1]))

    certificates = pd.read_csv(f"{DESTINATION_FOLDER}/{certificatesFiles[-1]}", sep=",", quotechar='"', lineterminator="\n")
    certificates["date"] = str(re.sub("Certificates_([0-9]{4}-[0-9]{2}-[0-9]{2}).csv", "\\1", certificatesFiles[-1]))

    # On concatène l'historique et les certificats du jour
    # On regarde les certificats qui ont plusieurs dates de fin.
    histo_and_new = pd.concat([certificates, histo])
    histo_and_new = histo_and_new.drop_duplicates(subset=histo_and_new.columns.difference(["date", "index"]))
    pd.DataFrame.to_csv(histo_and_new, "%s/History_%s.csv" % (DESTINATION_FOLDER, str(date.today())), index=False)

    # On sauve dans un fichier les potentiels doublons.
    dup = histo_and_new.drop_duplicates(["certificate", "valid_until"])
    boolean = dup.duplicated(["certificate"])
    dup = dup[boolean]
    pd.DataFrame.to_csv(dup, "%s/Duplicates_%s.csv" % (DESTINATION_FOLDER, str(date.today())), index=False)


def save_iscc_certificates(email: bool, batch: int) -> Tuple[int, list]:
    today = date.today()
    certificates = []
    filename = "%s/Certificates_%s.csv" % (DESTINATION_FOLDER, today.strftime("%Y-%m-%d"))
    df = pd.read_csv(filename, sep=",", quotechar='"', lineterminator="\n")

    df.fillna("", inplace=True)

    for _, row in df.iterrows():
        try:
            if "." in row["valid_from"]:
                row["valid_from"].split(".")
            elif "-" in row["valid_from"]:
                valid_from = datetime.strptime(row["valid_from"], "%Y-%m-%d").date()
            else:
                print("* Unrecognized date format [%s]" % (row["valid_from"]))
                print(row)
                valid_from = date(year=1970, month=1, day=1)
        except Exception:
            valid_from = date(year=1970, month=1, day=1)

        try:
            if "." in row["valid_until"]:
                vu = row["valid_until"].split(".")
                valid_until = date(year=2000 + int(vu[2]), month=int(vu[1]), day=int(vu[0]))
            elif "-" in row["valid_until"]:
                valid_until = datetime.strptime(row["valid_until"], "%Y-%m-%d").date()
            else:
                print("* Unrecognized date format [%s]" % (row["valid_until"]))
                print(row)
                valid_until = date(year=1970, month=1, day=1)
        except Exception:
            valid_until = date(year=1970, month=1, day=1)

        if "," in row["certificate_holder"]:
            holder = row["certificate_holder"].split(",")[0]
        else:
            holder = row["certificate_holder"]

        certificates.append(
            {
                "certificate_id": row["certificate"],
                "certificate_type": GenericCertificate.ISCC,
                "certificate_holder": holder,
                "certificate_issuer": row["issuing_cb"],
                "address": row["certificate_holder"],
                "valid_from": valid_from,
                "valid_until": valid_until,
                "scope": "%s" % (row["scope"]),
                "download_link": row["certificate_report"],
                "input": {"raw_material": row["raw_material"]},
                "output": "",
            }
        )

    existing, new = bulk_update_or_create(GenericCertificate, "certificate_id", certificates, batch)

    print("[ISCC Certificates] %d updated, %d created" % (len(existing), len(new)))
    return len(certificates), new


def send_email_summary(nb: int, new: list, email: bool) -> None:
    mail_content = "Güten Früden, <br />\n"
    mail_content += "La mise à jour des certificats ISCC s'est bien passée.<br />\n"
    mail_content += "%d certificats ont été chargés<br />\n" % (nb)

    if not len(new):
        mail_content += "Aucun nouveau certificat détecté<br />\n"
    else:
        for nc in new:
            mail_content += "Nouveau certificat ISCC détecté: [%s] - [%s]<br />\n" % (
                nc.certificate_id,
                nc.certificate_holder,
            )

    if email:
        try:
            connection = get_connection()
            connection.open()
            send_mail(
                "Certificats ISCC - %d certificats - %d nouveaux" % (nb, len(new)),
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


def get_wdtNonce() -> str:
    html_content = requests.get(ISCC_CERT_PAGE, headers=HEADERS).text
    soup = BeautifulSoup(html_content, "lxml")
    wdtNonceTag = soup.find("input", attrs={"name": "wdtNonceFrontendEdit_2"}).attrs
    wdtNonce: str = wdtNonceTag["value"]
    return wdtNonce, soup


def fetch_certificate_data(nonce: str, recordsTotal: int, test: bool, latest: bool) -> list:
    # On parcourt le tableau de résultats, en incrémentant de 1000 à chaque fois.
    # On stocke le tableau dans une liste de tableau
    allData: list = []
    start = 0
    if latest:
        start = recordsTotal - PAGELENGTH
    if test:
        recordsTotal = PAGELENGTH
    page = 1
    pages_total = round(recordsTotal / PAGELENGTH)
    print(f"> Loading {pages_total} pages of {PAGELENGTH} items")
    while start < recordsTotal:
        print(f"> From page {page} at index {start}")
        data = {"length": PAGELENGTH, "start": start, "draw": 1, "wdtNonce": nonce}
        r = requests.post(ISCC_DATA_URL, data=data, headers=HEADERS)
        certificates: dict = json.loads(r.content.decode("utf-8"))
        dataframe = pd.DataFrame.from_dict(certificates["data"])
        allData.append(dataframe)
        start = start + PAGELENGTH
        page += 1
    return allData


def clean_certificate_data(data: list, soup: BeautifulSoup) -> pd.DataFrame:
    allData = pd.concat(data)

    # print(allData.iloc[0])
    # 0     <span data-tooltip aria-haspopup="1" class="ha...
    # 1                            EU-ISCC-Cert-GR209-1271304
    # 2     <span data-tooltip aria-haspopup="1" class="ha...
    # 3     <span data-tooltip aria-haspopup="1" class="ha...
    # 4                                                   UCO
    # 5                                                  None
    # 6                                                  None
    # 7                                            2016-12-29
    # 8                                            2017-12-28
    # 9                                                  None
    # 10    <span data-tooltip aria-haspopup="1" class="ha...
    # 11    <a class="cert-map" href="https://www.google.c...
    # 12    <a class="cert-file" href=" https://certificat...
    # 13                                                 None
    # 14                                                   20
    ######## 2022-04-19: added column "products" after api change

    allData.columns = [
        "cert_status",
        "certificate",
        "certificate_holder",
        "scope",
        "raw_material",
        "addons",
        "products",
        "valid_from",
        "valid_until",
        "suspended",
        "issuing_cb",
        "map",
        "certificate_report",
        "audit_report",
        "unknown_column",
    ]

    # extraction de la balise HTML
    allData["certificate_holder"] = allData["certificate_holder"].str.replace('.*title="(.*)">.*', "\\1", regex=True)

    scope_definitions = get_scope_abbreviations(soup)
    allData["scope"] = allData["scope"].str.replace(
        r"<span[^>]*>(.*?)<\/span>", "\\1", regex=True
    )  # get html scope abbreviation
    allData["scope"] = allData["scope"].apply(
        get_full_scope_definitions, args=(scope_definitions,)
    )  # set full scope definition

    allData["raw_material"] = allData["raw_material"].str.replace('.*title="(.*)">.*', "\\1", regex=True)
    allData["issuing_cb"] = allData["issuing_cb"].str.replace('.*title="(.*)">.*', "\\1", regex=True)
    allData["map"] = allData["map"].str.replace('.*href="(.*)">.*', "\\1", regex=True)
    allData["certificate_report"] = allData["certificate_report"].str.replace('.*href="(.*)">.*', "\\1", regex=True)
    allData["audit_report"] = allData["audit_report"].str.replace('.*href="(.*)">.*', "\\1", regex=True)

    return cast(pd.DataFrame, allData)


# transform "BG, MB" into "Biogas plant, Biomethane plant"
def get_full_scope_definitions(abbreviations: str, scope_definitions: dict) -> str:
    abbreviations: list = abbreviations.split(", ")
    full_names = []
    for abbreviation in abbreviations:
        if abbreviation in scope_definitions:
            full_names.append(scope_definitions[abbreviation])
    return ", ".join(full_names)


def get_scope_abbreviations(soup: BeautifulSoup) -> list:
    content = soup.find(class_="wp-block-group__inner-container")
    definitions = content.find_all("sup")
    dic = {}
    for definition in definitions:
        text_parts = definition.get_text(strip=True).split("=")
        if len(text_parts) == 2:
            key = text_parts[0].strip()
            value = text_parts[1].strip()
            dic[key] = value

    return dic


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load ISCC certificates in database")
    parser.add_argument("--email", dest="email", action="store_true", default=False, help="Send a summary email")
    parser.add_argument("--latest", dest="latest", action="store_true", default=False, help="fetch latest certificates")
    parser.add_argument("--test", dest="test", action="store_true", default=False, help="Test mode")
    parser.add_argument("--batch", dest="batch", action="store", default=1000, help="Batch insert/update to database")
    args = parser.parse_args()

    update_iscc_certificates(args.email, args.test, args.latest, args.batch)
