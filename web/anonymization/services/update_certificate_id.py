# Update all columns related to a certificate_id to be anonymized
# CarbureLot.production_site_double_counting_certificate
# Site.dc_number
# Site.dc_reference
# DoubleCountingApplication.certificate_id
# DoubleCountingRegistration.certificate_id

import random

from anonymization.services.utils import anonymize_fields_and_collect_modifications, process_queryset_in_batches
from certificates.models import DoubleCountingRegistration
from core.models import CarbureLot
from doublecount.models import DoubleCountingApplication
from transactions.models import Site

# Global dictionary to store the mapping old_dc_number -> new_dc_number
dc_number_mapping = {}


def generate_dc_number():
    return str(random.randint(100000, 999999))


def find_and_replace_dc_number(certificate_id):
    # If the certificate id is not valid, return an empty string
    if certificate_id is None or certificate_id == "" or not certificate_id.startswith("FR_"):
        return ""

    # Extract the dc number from the certificate id
    extracted_dc_number = certificate_id.split("_")[1]

    # Get the new dc number from the mapping, if not found, generate a new one
    new_dc_number = dc_number_mapping.get(extracted_dc_number, generate_dc_number())

    return certificate_id.replace("FR_" + extracted_dc_number, "FR_" + new_dc_number)


def update_site_dc_reference(site):
    """
    Generates a random number for dc_number and builds dc_reference
    in the format FR_{dc_number}_{year} while preserving the existing year in dc_reference.
    Stores the mapping old_dc_number -> new_dc_number in the global dictionary.
    """
    # Save the old dc_number before modification
    dc_number = site.dc_number
    dc_reference = site.dc_reference

    # Extract the year from the existing dc_reference if available, otherwise generate a random year
    if site.dc_reference and site.dc_number:
        # Expected format: FR_{number}_{year}
        parts = site.dc_reference.split("_")
        if len(parts) >= 3:
            year = parts[-1]  # The last part is the year
        else:
            # If the format is not correct, generate a random year
            year = str(random.randint(2020, 2029))

        # Build dc_reference in the format FR_{dc_number}_{year}
        dc_number = str(random.randint(100000, 999999))
        dc_reference = f"FR_{dc_number}_{year}"

        # Store the mapping in the global dictionary
        dc_number_mapping[site.dc_number] = dc_number

    fields_to_anonymize = {
        "dc_number": dc_number,
        "dc_reference": dc_reference,
    }

    return anonymize_fields_and_collect_modifications(site, fields_to_anonymize)


def update_double_counting_registration_certificate_id(double_counting_registration):
    # Extract the dc number from the certificate id
    new_certificate_id = find_and_replace_dc_number(double_counting_registration.certificate_id)

    fields_to_anonymize = {"certificate_id": new_certificate_id}

    return anonymize_fields_and_collect_modifications(double_counting_registration, fields_to_anonymize)


def update_double_counting_application_certificate_id(double_counting_application):
    new_certificate_id = find_and_replace_dc_number(double_counting_application.certificate_id)
    fields_to_anonymize = {"certificate_id": new_certificate_id}

    return anonymize_fields_and_collect_modifications(double_counting_application, fields_to_anonymize)


def update_lot_production_site_double_counting_certificate(lot):
    new_certificate_id = find_and_replace_dc_number(lot.production_site_double_counting_certificate)
    fields_to_anonymize = {"production_site_double_counting_certificate": new_certificate_id}

    return anonymize_fields_and_collect_modifications(lot, fields_to_anonymize)


def update_certificate_ids(dry_run=False):
    """
    Updates the dc_number and dc_reference of sites.
    Returns a tuple containing the number of processed sites and the mapping dictionary.
    """
    # Reset the mapping dictionary
    global dc_number_mapping
    dc_number_mapping = {}

    sites = Site.objects.all()

    total_processed = process_queryset_in_batches(
        sites,
        update_site_dc_reference,
        batch_size=1000,
        model=Site,
        updated_fields=["dc_number", "dc_reference"],
        dry_run=dry_run,
    )

    # Update DoubleCountingRegistration.certificate_id
    double_counting_registrations = DoubleCountingRegistration.objects.all().exclude(
        certificate_id__isnull=True, certificate_id=""
    )

    total_processed2 = process_queryset_in_batches(
        double_counting_registrations,
        update_double_counting_registration_certificate_id,
        batch_size=1000,
        model=DoubleCountingRegistration,
        updated_fields=["certificate_id"],
        dry_run=dry_run,
    )

    # Update DoubleCountingApplication.certificate_id
    double_counting_applications = DoubleCountingApplication.objects.all().exclude(
        certificate_id="", certificate_id__isnull=True
    )

    total_processed3 = process_queryset_in_batches(
        double_counting_applications,
        update_double_counting_application_certificate_id,
        batch_size=1000,
        model=DoubleCountingApplication,
        updated_fields=["certificate_id"],
        dry_run=dry_run,
    )

    # Update CarbureLot.production_site_double_counting_certificate
    lots = CarbureLot.objects.all().exclude(
        production_site_double_counting_certificate="", production_site_double_counting_certificate__isnull=True
    )
    total_processed4 = process_queryset_in_batches(
        lots,
        update_lot_production_site_double_counting_certificate,
        batch_size=1000,
        model=CarbureLot,
        updated_fields=["production_site_double_counting_certificate"],
        dry_run=dry_run,
    )

    return total_processed + total_processed2 + total_processed3 + total_processed4
