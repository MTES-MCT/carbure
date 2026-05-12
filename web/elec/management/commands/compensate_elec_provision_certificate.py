import json
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import Exists, ExpressionWrapper, F, FloatField, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Round

from elec.models import ElecCertificateReadjustment, ElecProvisionCertificate


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
      1) Repartir de l'énergie non renouvelable par certificat:
           non_renewable_i = renewable_energy_i / enr_ratio_i
      2) Agréger par CPO/année :
           total_non_renewable = somme(non_renewable_i)
           total_renewable = somme(renewable_energy_i)
      3) Retrancher les réajustements annuels (même CPO, même année) du total non_renewable :
           non_renewable_net = total_non_renewable - total_non_renewable_readjustments
      4) Appliquer le nouveau ratio puis retirer le déjà-certifié renouvelable :
           delta = non_renewable_net * enr_nouveau - total_renewable

    Cette approche est robuste si un CPO a plusieurs certificats avec des enr_ratio différents.
    """
    # Étape A — Ne pas recréer une compensation annuelle déjà présente (clé métier : même CPO, année, source).
    compensation_certificates = ElecProvisionCertificate.objects.filter(
        year=year,
        source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
        cpo_id=OuterRef("cpo_id"),
    )

    # Étape B — Formule du delta sur base "non_renewable" (voir docstring).
    #   non_renewable_net = total_non_renewable_energy - total_non_renewable_readjustments
    #   delta = non_renewable_net * new_enr_ratio - total_energy_certificates
    delta_expression = ExpressionWrapper(
        ((F("total_non_renewable_energy") - F("total_non_renewable_readjustments")) * Value(new_enr_ratio))
        - F("total_energy_certificates"),
        output_field=FloatField(),
    )

    # Étape C — Total des réajustements non-renouvelables (MWh) pour ce CPO et cette année.
    readjustments_for_year = (
        ElecCertificateReadjustment.objects.filter(
            cpo_id=OuterRef("cpo_id"),
            year=year,
        )
        .values("cpo_id")
        .annotate(total=Sum("non_renewable_energy_amount"))
        .values("total")[:1]
    )

    # Étape D — Filtre des lignes certificat éligibles, puis agrégation par (cpo_id, nom, année).
    #   - exclusion des sources hors périmètre et des ratios invalides ;
    #   - somme des energy_amount/enr_ratio → total_non_renewable_energy ;
    #   - somme des energy_amount → total_energy_certificates ;
    #   - jointure logique du total des réajustements non-renouvelables → total_non_renewable_readjustments ;
    #   - application de delta_expression puis arrondi à 2 décimales.
    # Étape E — Ne garder que les CPO où la compensation est strictement positive.
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
                Subquery(readjustments_for_year, output_field=FloatField()),
                Value(0.0),
            ),
            total_non_renewable_energy=Sum(
                ExpressionWrapper(F("energy_amount") / F("enr_ratio"), output_field=FloatField())
            ),
        )
        .annotate(total_energy_certificates=Sum(F("energy_amount")))
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
