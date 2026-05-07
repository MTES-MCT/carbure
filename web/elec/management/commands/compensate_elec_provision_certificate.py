import json
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Exists, ExpressionWrapper, F, FloatField, OuterRef, Value
from django.db.models.functions import Round

from elec.models import ElecProvisionCertificate


def _build_compensation_certificate(cpo_id, quarter, year, operating_unit, energy_amount, new_enr_ratio, cpo_name=None):
    certificate = ElecProvisionCertificate(
        cpo_id=cpo_id,
        quarter=quarter,
        year=year,
        operating_unit=operating_unit,
        energy_amount=energy_amount,
        enr_ratio=new_enr_ratio,
        source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
    )
    certificate.cpo_name = cpo_name
    return certificate


def _get_certificates_with_delta(year, new_enr_ratio):
    compensation_certificates = ElecProvisionCertificate.objects.filter(
        year=year,
        source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
        cpo_id=OuterRef("cpo_id"),
        quarter=OuterRef("quarter"),
        operating_unit=OuterRef("operating_unit"),
    )

    delta_expression = ExpressionWrapper(
        ((F("energy_amount") / F("enr_ratio")) * Value(new_enr_ratio)) - F("energy_amount"),
        output_field=FloatField(),
    )

    return (
        ElecProvisionCertificate.objects.filter(year=year)
        .exclude(
            source__in=[
                ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
                ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION,
            ]
        )
        .annotate(has_compensation=Exists(compensation_certificates))
        .filter(has_compensation=False)
        .exclude(enr_ratio__isnull=True)
        .exclude(enr_ratio=0)
        .values(
            "cpo_id",
            "cpo__name",
            "quarter",
            "year",
            "operating_unit",
        )
        .annotate(delta=Round(delta_expression, 2))
        .filter(delta__gt=0)
    )


def _build_compensation_certificates(certificates_with_delta, new_enr_ratio):
    return [
        _build_compensation_certificate(
            cpo_id=certificate["cpo_id"],
            quarter=certificate["quarter"],
            year=certificate["year"],
            operating_unit=certificate["operating_unit"],
            energy_amount=certificate["delta"],
            new_enr_ratio=new_enr_ratio,
            cpo_name=certificate["cpo__name"],
        )
        for certificate in certificates_with_delta
    ]


def _get_compensation_certificates_to_create(year, new_enr_ratio):
    certificates_with_delta = _get_certificates_with_delta(year, new_enr_ratio)
    return _build_compensation_certificates(certificates_with_delta, new_enr_ratio)


def _log_compensation_summary(stdout, certificates):
    summary_by_cpo = defaultdict(lambda: {"name": None, "certificates": 0, "energy_amount": 0.0})
    for certificate in certificates:
        cpo_summary = summary_by_cpo[certificate.cpo_id]
        if not cpo_summary["name"]:
            cpo_summary["name"] = getattr(certificate, "cpo_name", None)
        cpo_summary["certificates"] += 1
        cpo_summary["energy_amount"] += float(certificate.energy_amount)

    total_energy_amount = sum(data["energy_amount"] for data in summary_by_cpo.values())
    stdout.write(f"Total energy amount: {round(float(total_energy_amount), 2)} MWh")

    for cpo_id, data in sorted(summary_by_cpo.items(), key=lambda item: item[1]["energy_amount"], reverse=True):
        stdout.write(
            " - "
            f"{data['name'] or f'CPO #{cpo_id}'} | "
            f"certificates={data['certificates']} | "
            f"energy_amount={round(float(data['energy_amount']), 2)} MWh"
        )


def _build_result_payload(certificates):
    return [
        {
            "cpo_id": c.cpo_id,
            "quarter": c.quarter,
            "year": c.year,
            "operating_unit": c.operating_unit,
            "energy_amount": c.energy_amount,
            "source": c.source,
        }
        for c in certificates
    ]


class Command(BaseCommand):
    help = "Compensate elec provision certificate"

    def add_arguments(self, parser):
        parser.add_argument(
            "--enr_ratio",
            type=float,
            help="Current ENR ratio",
            required=True,
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Apply the compensation",
        )
        parser.add_argument(
            "--log",
            action="store_true",
            default=True,
            help="Log the compensation",
        )
        parser.add_argument(
            "--year",
            type=int,
            help="Year to compensate",
            required=True,
        )

    def handle(self, *args, **options):
        enr_ratio = options["enr_ratio"]
        year = options["year"]
        if options["log"]:
            print(f" -- Running with ENR ratio = {enr_ratio}%.")

        new_enr_ratio = enr_ratio / 100  # 25 -> 0.25

        elec_provision_certificates = _get_compensation_certificates_to_create(year, new_enr_ratio)

        if options["log"]:
            _log_compensation_summary(self.stdout, elec_provision_certificates)

        if options["apply"]:
            if elec_provision_certificates:
                ElecProvisionCertificate.objects.bulk_create(elec_provision_certificates, batch_size=1000)
                if options["log"]:
                    print(f"Created {len(elec_provision_certificates)} new certificates")
            elif options["log"]:
                print("No new certificates to create")

        return json.dumps(_build_result_payload(elec_provision_certificates))
