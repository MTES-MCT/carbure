from django.db import models
from django.db.models import Q
from rest_framework import serializers

from core.models import Entity
from elec.models import ElecProvisionCertificate, ElecProvisionCertificateQualicharge
from elec.repositories.meter_reading_repository import MeterReadingRepository


def handle_bulk_create_validation_errors(request, serializer):
    errors = []
    for idx, (item_errors, item_data) in enumerate(zip(serializer.errors, request.data)):
        if not item_errors:
            continue

        entity = item_data.get("entity", "")
        siren = item_data.get("siren", "")

        # Errors at entity level
        for field, messages in item_errors.items():
            if field != "operational_units":
                errors.append({"index": idx, "entity": entity, "siren": siren, "field": field, "errors": messages})

        # Errors at operational unit level
        if "operational_units" in item_errors:
            operational_units = item_data.get("operational_units", [])
            for unit_error, unit_data in zip(item_errors["operational_units"], operational_units):
                if not unit_error:
                    continue

                code = unit_data.get("code", "")

                for field, messages in unit_error.items():
                    if field != "stations":
                        errors.append(
                            {"index": idx, "entity": entity, "unit_code": code, "field": field, "errors": messages}
                        )

                # Errors at station level
                if "stations" in unit_error:
                    stations = unit_data.get("stations", [])
                    for station_error, station_data in zip(unit_error["stations"], stations):
                        if not station_error:
                            continue

                        station_id = station_data.get("id", "")

                        for field, messages in station_error.items():
                            errors.append(
                                {
                                    "index": idx,
                                    "entity": entity,
                                    "unit_code": code,
                                    "station_id": station_id,
                                    "field": field,
                                    "errors": messages,
                                }
                            )

    raise serializers.ValidationError({"status": "validation_error", "errors": errors})


def resolve_cpo(siren):
    """
    Resolve CPO entity from SIREN, handling duplicates by selecting the master entity.

    Returns:
        tuple: (cpo_entity, unknown_siren)
            - If entity found: (Entity, None)
            - If not found: (None, siren)
            - If multiple found and master exists: (master_Entity, None)
            - If multiple found but no master: (None, siren)
    """
    try:
        return Entity.objects.get(registration_id=siren, entity_type=Entity.CPO, is_enabled=True), None
    except Entity.DoesNotExist:
        return None, siren
    except Entity.MultipleObjectsReturned:
        try:
            return Entity.objects.get(registration_id=siren, entity_type=Entity.CPO, is_master=True, is_enabled=True), None
        except Entity.DoesNotExist:
            return None, siren


def process_certificates_batch(validated_data, double_validated):
    """
    Process a batch of certificates and create/update Qualicharge provision certificates.

    Args:
        validated_data: List of validated items from serializer
        double_validated: Set of (station_id, date_from, date_to) already double-validated

    Returns:
        list: List of error dictionaries for certificates that failed to process
    """
    errors = []
    certificates_to_create = []
    certificates_to_update = []

    # Collect all station_ids to fetch existing certificates in one query
    all_station_keys = []
    for item in validated_data:
        for unit in item["operational_units"]:
            for station in unit.get("stations", []):
                station_id = station["id"]
                date_from = unit["from"]
                date_to = unit["to"]
                all_station_keys.append((station_id, date_from, date_to))

    # Fetch existing certificates in one query
    existing_certs = {}
    if all_station_keys:
        query = Q()
        for station_id, date_from, date_to in all_station_keys:
            query |= Q(station_id=station_id, date_from=date_from, date_to=date_to)

        for cert in ElecProvisionCertificateQualicharge.objects.filter(query):
            existing_certs[(cert.station_id, cert.date_from, cert.date_to)] = cert

    # Prepare bulk operations
    for item in validated_data:
        siren = item["siren"]
        cpo, unknown_siren = resolve_cpo(siren)

        for unit in item["operational_units"]:
            unit_errors = _prepare_certificates_bulk(
                unit, cpo, unknown_siren, double_validated, existing_certs, certificates_to_create, certificates_to_update
            )
            errors.extend(unit_errors)

    # Execute bulk operations
    if certificates_to_create:
        ElecProvisionCertificateQualicharge.objects.bulk_create(certificates_to_create, batch_size=100)

    if certificates_to_update:
        ElecProvisionCertificateQualicharge.objects.bulk_update(
            certificates_to_update,
            ["cpo", "unknown_siren", "year", "operating_unit", "energy_amount", "is_controlled_by_qualicharge"],
            batch_size=100,
        )

    return errors


def _prepare_certificates_bulk(unit, cpo, unknown_siren, double_validated, existing_certs, to_create, to_update):
    """
    Prepare certificates for bulk create/update operations.

    Args:
        unit: Operational unit data
        cpo: Resolved CPO entity (can be None)
        unknown_siren: SIREN that couldn't be resolved (can be None)
        double_validated: Set of already double-validated certificates
        existing_certs: Dict of existing certificates by (station_id, date_from, date_to)
        to_create: List to append new certificates
        to_update: List to append certificates to update

    Returns:
        list: List of error dictionaries for stations that failed to process
    """
    errors = []
    code = unit["code"]
    date_from = unit["from"]
    date_to = unit["to"]
    year = date_from.year
    enr_ratio = MeterReadingRepository.get_renewable_share(year)

    for station in unit.get("stations", []):
        station_id = station["id"]

        # Check if already double-validated
        if (station_id, date_from, date_to) in double_validated:
            errors.append({"station_id": station_id, "error": "Provision certificate already validated and created"})
            continue

        try:
            key = (station_id, date_from, date_to)

            if key in existing_certs:
                # Update existing certificate
                cert = existing_certs[key]
                cert.cpo = cpo
                cert.unknown_siren = unknown_siren
                cert.year = year
                cert.operating_unit = code
                cert.energy_amount = station["energy"]
                cert.is_controlled_by_qualicharge = station["is_controlled"]
                to_update.append(cert)
            else:
                # Create new certificate
                to_create.append(
                    ElecProvisionCertificateQualicharge(
                        station_id=station_id,
                        date_from=date_from,
                        date_to=date_to,
                        cpo=cpo,
                        unknown_siren=unknown_siren,
                        year=year,
                        operating_unit=code,
                        energy_amount=station["energy"],
                        is_controlled_by_qualicharge=station["is_controlled"],
                        enr_ratio=enr_ratio,
                    )
                )
        except Exception as e:
            errors.append({"station_id": station_id, "error": str(e)})

    return errors


def create_provision_certificates_from_qualicharge(qualicharge_certificates):
    """
    Create provision certificates from Qualicharge data if validated_by is BOTH.
    Groups certificates by CPO, operating unit, and date range, then creates
    corresponding provision certificates.
    """
    BOTH = ElecProvisionCertificateQualicharge.BOTH

    # Group certificates and calculate total energy amounts
    grouped_certificates = (
        qualicharge_certificates.values("cpo", "operating_unit", "date_from", "date_to", "year")
        .filter(validated_by=BOTH)
        .annotate(total_energy_amount=models.Sum("energy_amount"))
        .order_by("cpo", "operating_unit", "date_from", "date_to")
    )

    provision_certificates_to_create = []
    for q_certificate in grouped_certificates:
        provision_certificates_to_create.append(
            ElecProvisionCertificate(
                cpo_id=q_certificate["cpo"],
                operating_unit=q_certificate["operating_unit"],
                energy_amount=q_certificate["total_energy_amount"],
                quarter=(q_certificate["date_from"].month - 1) // 3 + 1,
                year=q_certificate["year"],
                remaining_energy_amount=q_certificate["total_energy_amount"],
                source=ElecProvisionCertificate.QUALICHARGE,
            )
        )

    ElecProvisionCertificate.objects.bulk_create(provision_certificates_to_create)
