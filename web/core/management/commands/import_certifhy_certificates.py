from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError

from core.models import GenericCertificate

CERTIFHY_CERTIFICATES_URL = "https://www.certifhy.eu/certificates-non-conformity-databases/"
REQUEST_TIMEOUT = 60

STATUS_MAPPING = {
    "valid": GenericCertificate.VALID,
    "suspended": GenericCertificate.SUSPENDED,
    "withdrawn": GenericCertificate.WITHDRAWN,
    "terminated": GenericCertificate.TERMINATED,
    "expired": GenericCertificate.EXPIRED,
}


class Command(BaseCommand):
    help = "Import certificates from the CertifHy public certificate database"

    def handle(self, *args, **options):
        html = fetch_certificates_page()
        certificates = parse_certificates(html)
        certificates_by_status = defaultdict(list)

        for certificate in certificates:
            certificates_by_status[certificate["status"]].append(certificate)

        created_count = 0
        updated_count = 0
        for status, status_certificates in certificates_by_status.items():
            updated, created = GenericCertificate.bulk_create_or_update(status_certificates, status)
            updated_count += len(updated)
            created_count += len(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(certificates)} CertifHy certificates: " f"{created_count} created, {updated_count} updated"
            )
        )


def fetch_certificates_page():
    try:
        response = requests.get(CERTIFHY_CERTIFICATES_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CommandError(f"Could not fetch CertifHy certificates: {exc}") from exc

    return response.text


def normalize_text(value):
    return " ".join(value.split()).strip() if value else ""


def card_fields(card):
    fields = {}
    for label in card.select("span.font-semibold"):
        value = label.find_next_sibling()
        if value:
            fields[normalize_text(label.get_text()).removesuffix(":")] = normalize_text(value.get_text())
    return fields


def parse_date(value):
    return datetime.strptime(value, "%d/%m/%Y").date()


def certificate_link(card):
    for link in card.select("a[href]"):
        if normalize_text(link.get_text()).lower() == "certificate":
            return link["href"]
    return None


def parse_certificate(card):
    fields = card_fields(card)
    status = STATUS_MAPPING.get(fields.get("Status", "").lower())
    if status is None:
        raise ValueError(f"unknown status: {fields.get('Status')}")

    return {
        "certificate_id": fields["Certificate ID"],
        "certificate_type": GenericCertificate.CERTIFHY,
        "certificate_holder": fields["Certificate Holder"],
        "certificate_issuer": fields.get("Issuing CB", ""),
        "address": "",
        "valid_from": parse_date(fields["Valid From"]),
        "valid_until": parse_date(fields["Valid Until"]),
        "download_link": certificate_link(card),
        "scope": fields.get("Scope", ""),
        "input": None,
        "output": {"products": fields.get("Products", "")},
        "status": status,
    }


def parse_certificates(html):
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select(".js-cert-card")
    if not cards:
        raise CommandError("No CertifHy certificates found on the page")

    try:
        return [parse_certificate(card) for card in cards]
    except (KeyError, ValueError) as exc:
        raise CommandError(f"Could not parse a CertifHy certificate: {exc}") from exc
