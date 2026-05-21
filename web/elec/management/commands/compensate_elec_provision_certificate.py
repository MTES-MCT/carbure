import json
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Exists, ExpressionWrapper, F, FloatField, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Round

from elec.models import ElecCertificateReadjustment, ElecProvisionCertificate


class Command(BaseCommand):
    # python web/manage.py compensate_elec_provision_certificate --enr_ratio 30.81 --log --year 2025
    help = "Compensate elec provision certificate"

    def add_arguments(self, parser):
        parser.add_argument(
            "--enr_ratio",
            type=float,
            help="Current ENR ratio in % (ex: 25 for 25%)",
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
    """
    Calcule, par CPO et pour une année donnée, le volume de compensation ENR (MWh renouvelable)
    à créer en une requête agrégée.

    Idée métier :
      1) Repartir de l'énergie non renouvelable par certificat et réajustement:
           non_renewable_i = renewable_energy_i / enr_ratio_i
      2) Agréger par CPO/année séparément pour certificats et réajustements
      3) Calculer le delta renouvelable de chaque bloc avec le nouveau ratio :
           delta_certificats = total_non_renewable_certificats * enr_nouveau - total_renewable_certificats
           delta_readjustments = total_non_renewable_readjustments * enr_nouveau - total_renewable_readjustments
      4) Compensation nette = delta_certificats - delta_readjustments

    """
    # Étape A — Ne pas recréer une compensation annuelle déjà présente (clé métier : même CPO, année, source).
    compensation_certificates = ElecProvisionCertificate.objects.filter(
        year=year,
        source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
        cpo_id=OuterRef("cpo_id"),
    )

    # Étape B — Formule du delta (voir docstring).
    #   delta = (non_renewable_certificates * new_ratio - renewable_certificates) -
    # (non_renewable_readjustments * new_ratio - renewable_readjustments)
    delta_expression = ExpressionWrapper(
        (F("total_non_renewable_certificates") * Value(new_enr_ratio) - F("total_renewable_certificates"))
        - (F("total_non_renewable_readjustments") * Value(new_enr_ratio) - F("total_renewable_readjustments")),
        output_field=FloatField(),
    )

    # Étape C — Totaux des réajustements (MWh) pour ce CPO et cette année.
    readjustments_non_renewable_for_year = (
        ElecCertificateReadjustment.objects.filter(
            cpo_id=OuterRef("cpo_id"),
            year=year,
        )
        .values("cpo_id")
        .annotate(total=Sum(F("energy_amount") / F("enr_ratio")))
        .values("total")[:1]
    )
    readjustments_renewable_for_year = (
        ElecCertificateReadjustment.objects.filter(
            cpo_id=OuterRef("cpo_id"),
            year=year,
        )
        .values("cpo_id")
        .annotate(total=Sum("energy_amount"))
        .values("total")[:1]
    )

    # Étape D — Récupération des certificats sur lesquels appliquer un rattrapage ENR
    q = (
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
        .values("cpo_id", "cpo__name", "year")
        .annotate(
            total_non_renewable_readjustments=Coalesce(
                Subquery(readjustments_non_renewable_for_year, output_field=FloatField()),
                Value(0.0),
            ),
            total_renewable_readjustments=Coalesce(
                Subquery(readjustments_renewable_for_year, output_field=FloatField()),
                Value(0.0),
            ),
            total_non_renewable_certificates=Sum(
                ExpressionWrapper(F("energy_amount") / F("enr_ratio"), output_field=FloatField())
            ),
        )
        .annotate(total_renewable_certificates=Sum(F("energy_amount")))
        .annotate(delta=Round(delta_expression, 2))
        .filter(delta__gt=0)
    )

    return q


def _build_compensation_certificates(certificates_with_delta, new_enr_ratio):
    return [
        _build_compensation_certificate(
            cpo_id=certificate["cpo_id"],
            quarter=1,
            year=certificate["year"],
            operating_unit="ALL",
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
