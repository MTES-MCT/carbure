from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.models import GenericCertificate

ISCC_CERTIFICATES_URL = "https://iscc-system.org/wp-json/api/certificates"
ISCC_CERTIFICATES_PAGE_URL = "https://www.iscc-system.org/certificates/all-certificates/"
ISCC_PAGE_SIZE = 200
REQUEST_TIMEOUT = 60

ISCC_STATUS_MAPPING = {
    "valid": GenericCertificate.VALID,
    "suspended": GenericCertificate.SUSPENDED,
    "terminated": GenericCertificate.TERMINATED,
    "withdrawn": GenericCertificate.WITHDRAWN,
}


class Command(BaseCommand):
    help = "Import ISCC certificates from the ISCC public certificates API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--statuses",
            default=",".join(ISCC_STATUS_MAPPING.keys()),
            help="Comma-separated ISCC statuses to import",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch and parse certificates without writing to the database",
        )
        parser.add_argument(
            "--latest",
            type=int,
            default=None,
            help="Only import the latest N certificates for each scraped ISCC status",
        )
        parser.add_argument(
            "--email",
            action="store_true",
            help="Send an import summary email to Carbure admins",
        )

    def handle(self, *args, **options):
        statuses = read_statuses_arg(options["statuses"])
        dry_run = options["dry_run"]
        latest = read_latest_arg(options["latest"])
        should_send_email = options["email"]

        total_parsed = 0
        total_created = 0
        total_updated = 0
        total_skipped = 0
        total_expired = 0
        new_certificates = []

        self.stdout.write("> Importing ISCC certificates...")

        scope_definitions = fetch_scope_definitions()

        for iscc_status in statuses:
            django_status = ISCC_STATUS_MAPPING[iscc_status]
            status_parsed = 0
            status_created = 0
            status_updated = 0
            status_skipped = 0
            page = 1
            max_pages = 1
            pages_fetched = 0
            total_count = 0

            while page <= max_pages and (latest is None or status_parsed < latest):
                html, total_count, max_pages = fetch_iscc_html(iscc_status, page)
                pages_fetched += 1
                remaining = None if latest is None else latest - status_parsed
                certificates, errors = parse_certificates_html(html, django_status, remaining, scope_definitions)

                status_parsed += len(certificates)
                status_skipped += len(errors)

                if not dry_run:
                    existing, new = GenericCertificate.bulk_create_or_update(certificates, django_status)
                    status_updated += len(existing)
                    status_created += len(new)
                    new_certificates.extend(new)

                page += 1

            total_parsed += status_parsed
            total_skipped += status_skipped
            total_updated += status_updated
            total_created += status_created

            self.stdout.write(
                f"> {iscc_status}: parsed {status_parsed} certificates"
                f" from {total_count} ISCC results across {pages_fetched} pages"
            )

            if status_skipped:
                self.stdout.write(self.style.WARNING(f"> {iscc_status}: skipped {status_skipped} malformed certificates"))

            if not dry_run:
                self.stdout.write(f"> {iscc_status}: {status_updated} updated, {status_created} created")

        total_expired = expire_saved_iscc_certificates(dry_run)
        self.stdout.write(f"> expired: {total_expired} existing ISCC certificates marked as expired")

        if dry_run:
            self.stdout.write(f"> Dry run complete: {total_parsed} parsed, {total_skipped} skipped")
        else:
            self.stdout.write(
                f"> Import complete: {total_updated} updated, {total_created} created,"
                f" {total_expired} expired, {total_skipped} skipped"
            )

        if should_send_email:
            send_email_summary(
                parsed=total_parsed,
                updated=total_updated,
                created=total_created,
                expired=total_expired,
                skipped=total_skipped,
                new_certificates=new_certificates,
                dry_run=dry_run,
            )


def read_statuses_arg(statuses):
    parsed_statuses = [status.strip().lower() for status in statuses.split(",") if status.strip()]
    unknown_statuses = [status for status in parsed_statuses if status not in ISCC_STATUS_MAPPING]

    if unknown_statuses:
        valid_statuses = ", ".join(ISCC_STATUS_MAPPING.keys())
        raise CommandError(f"Unknown ISCC status: {', '.join(unknown_statuses)}. Valid statuses: {valid_statuses}")

    if not parsed_statuses:
        raise CommandError("At least one ISCC status must be provided")

    return parsed_statuses


def read_latest_arg(latest):
    if latest is not None and latest <= 0:
        raise CommandError("--latest must be greater than 0")
    return latest


def expire_saved_iscc_certificates(dry_run=False):
    today = timezone.localdate()

    expired_certificates = GenericCertificate.objects.filter(
        certificate_type=GenericCertificate.ISCC,
        status__in=[GenericCertificate.PENDING, GenericCertificate.VALID],
        valid_until__lt=today,
    )

    if dry_run:
        return expired_certificates.count()

    return expired_certificates.update(status=GenericCertificate.EXPIRED, last_status_update=today)


def send_email_summary(parsed, updated, created, expired, skipped, new_certificates, dry_run=False):
    subject_prefix = "[DRY RUN] " if dry_run else ""
    subject = f"{subject_prefix}Certificats ISCC - {parsed} chargés - {created} nouveaux"

    lines = [
        "Bonjour,",
        "",
        "La mise à jour des certificats ISCC s'est terminée.",
        "",
        f"Certificats chargés: {parsed}",
        f"Certificats mis à jour: {updated}",
        f"Certificats créés: {created}",
        f"Certificats expirés localement: {expired}",
        f"Certificats ignorés car mal formés: {skipped}",
        "",
    ]

    if not new_certificates:
        lines.append("Aucun nouveau certificat détecté.")
    else:
        lines.append("Nouveaux certificats détectés:")
        for certificate in new_certificates:
            lines.append(f"- {certificate.certificate_id} - {certificate.certificate_holder}")

    send_mail(
        subject,
        "\n".join(lines),
        settings.DEFAULT_FROM_EMAIL,
        ["carbure@beta.gouv.fr"],
        fail_silently=False,
    )


def normalize_text(value):
    if value is None:
        return ""

    text = " ".join(str(value).split()).strip()
    return "" if text == "-" else text


def parse_iscc_date(value):
    return datetime.strptime(normalize_text(value), "%d.%m.%y").date()


def parse_fold_value(card, label):
    for item in card.select(".is-certificate-fold-item"):
        title = item.select_one(".title")
        if normalize_text(title.get_text(" ", strip=True) if title else "") != label:
            continue

        values = [p for p in item.find_all("p", recursive=False) if "title" not in p.get("class", [])]
        if not values:
            return ""

        if label == "Issuing CB":
            titled_element = values[0].select_one("[title]")
            if titled_element:
                return normalize_text(titled_element.get("title"))

        return normalize_text(values[0].get_text(" ", strip=True))

    return ""


def parse_certificate_link(card):
    for link in card.select("a[href]"):
        link_labels = {normalize_text(text) for text in link.stripped_strings}
        if "Certificate" in link_labels:
            return normalize_text(link.get("href"))
    return None


def fetch_scope_definitions():
    try:
        response = requests.get(ISCC_CERTIFICATES_PAGE_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return {}

    return parse_scope_definitions(response.text)


def parse_scope_definitions(html):
    soup = BeautifulSoup(html or "", "lxml")
    content = soup.find(class_="wp-block-group__inner-container")
    if not content:
        return {}

    definitions = {}
    for strong_tag in content.find_all("strong"):
        abbreviation, definition = parse_scope_definition(strong_tag)
        if abbreviation and definition:
            definitions[abbreviation] = definition

    return definitions


def parse_scope_definition(strong_tag):
    strong_text = normalize_text(strong_tag.get_text(" ", strip=True))

    if "=" in strong_text:
        abbreviation, definition_start = strong_text.split("=", 1)
        definition = definition_start or read_definition_after_tag(strong_tag)
        return normalize_text(abbreviation), normalize_text(definition)

    next_text = read_definition_after_tag(strong_tag)
    if "=" not in next_text:
        return strong_text, ""

    _, definition = next_text.split("=", 1)
    return strong_text, normalize_text(definition)


def read_definition_after_tag(tag):
    parts = []
    sibling = tag.next_sibling

    while sibling is not None and getattr(sibling, "name", None) != "br":
        if getattr(sibling, "name", None) == "strong":
            break

        parts.append(sibling.get_text(" ", strip=True) if hasattr(sibling, "get_text") else str(sibling))
        sibling = sibling.next_sibling

    return normalize_text(" ".join(parts))


def expand_scope(scope, definitions):
    scope_items = [normalize_text(item) for item in scope.split(",") if normalize_text(item)]
    if not scope_items:
        return ""

    return ", ".join(definitions.get(item, item) for item in scope_items)


def parse_certificate_card(card, status, scope_definitions=None):
    certificate_id = normalize_text(card.select_one(".tag").get_text(" ", strip=True) if card.select_one(".tag") else "")

    date_tag = card.select_one(".date")
    date_parts = normalize_text(date_tag.get_text(" ", strip=True) if date_tag else "").split("–")
    if len(date_parts) != 2:
        raise ValueError("missing validity dates")

    holder_tag = card.select_one("h3 span[title]") or card.select_one("h3")
    if holder_tag and holder_tag.has_attr("title"):
        address = normalize_text(holder_tag.get("title"))
    elif holder_tag:
        address = normalize_text(holder_tag.get_text(" ", strip=True))
    else:
        address = ""
    certificate_holder = normalize_text(address.split(",", 1)[0])

    valid_from = parse_iscc_date(date_parts[0])
    valid_until = parse_iscc_date(date_parts[1])

    if not certificate_id:
        raise ValueError("missing certificate id")
    if not certificate_holder:
        raise ValueError("missing certificate holder")

    return {
        "certificate_id": certificate_id,
        "certificate_type": GenericCertificate.ISCC,
        "certificate_holder": certificate_holder,
        "certificate_issuer": parse_fold_value(card, "Issuing CB"),
        "address": address,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "download_link": parse_certificate_link(card),
        "scope": expand_scope(parse_fold_value(card, "Scope"), scope_definitions or {}),
        "input": {"raw_material": parse_fold_value(card, "Raw Material")},
        "output": {"products": parse_fold_value(card, "Products")},
        "status": status,
    }


def parse_certificates_html(html, status, max_certificates=None, scope_definitions=None):
    soup = BeautifulSoup(html or "", "lxml")
    certificates = []
    errors = []

    for index, card in enumerate(soup.select(".is-certificate"), start=1):
        if max_certificates is not None and len(certificates) >= max_certificates:
            break

        try:
            certificates.append(parse_certificate_card(card, status, scope_definitions))
        except (AttributeError, ValueError) as exc:
            errors.append({"index": index, "error": str(exc)})

    return certificates, errors


def build_payload(status, page):
    return {
        "filters": {"status": [status]},
        "valid_from": "",
        "valid_until": "",
        "search": "",
        "count": ISCC_PAGE_SIZE,
        "page": page,
    }


def fetch_iscc_html(status, page):
    try:
        response = requests.post(
            ISCC_CERTIFICATES_URL,
            json=build_payload(status, page),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise CommandError(f"Could not fetch ISCC certificates for status {status} page {page}: {exc}") from exc
    except ValueError as exc:
        raise CommandError(f"Invalid JSON response from ISCC for status {status} page {page}") from exc

    if not payload.get("success"):
        raise CommandError(f"ISCC API returned an unsuccessful response for status {status} page {page}")

    try:
        data = payload["data"]["data"]
    except (KeyError, TypeError) as exc:
        raise CommandError(f"Unexpected ISCC response format for status {status} page {page}") from exc

    return data.get("html") or "", int(data.get("totalCount") or 0), int(data.get("maxPages") or 1)
