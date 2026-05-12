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

    Idée métier (toutes les quantités ci-dessous sont en MWh *renouvelable* sauf mention) :
      1) On somme l'énergie des certificats de base du CPO sur l'année (hors compensation / erreur admin).
      2) On retranche la somme des réajustements déjà enregistrés pour ce CPO et cette année
         (champ year sur elec_certificate_readjustment). C'est la base *nette* après remboursements.
      3) On applique le changement de ratio ENR sur cette base nette :
           delta = (net / enr_ancien) * enr_nouveau - net

    Exemple chiffré (enr ancien = 0,25 = 25 %, enr nouveau = 0,30 = 30 %) :
      - Total certificats renouvelable = 100 ; réajustements = 90 → net = 10 MWh.
      - 10 / 0,25 = 40
      - 40 * 0,30 = 12 MWh renouvelable « attendu » au nouveau ratio pour ce bloc
      - delta compensation = 12 - 10 = 2 MWh (c’est ce qu’on crée sur le certificat de rattrapage).

    Limite du modèle agrégé : la requête suppose un seul enr_ratio pertinent par ligne de groupement
    . Si un même CPO mélange des certificats avec des enr_ratio différents,
    le calcul devrait être fait ligne à ligne puis sommé (fenêtre / sous-requête par certificat).
    """
    # Étape A — Ne pas recréer une compensation annuelle déjà présente (clé métier : même CPO, année, source).
    compensation_certificates = ElecProvisionCertificate.objects.filter(
        year=year,
        source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
        cpo_id=OuterRef("cpo_id"),
    )

    # Étape B — Formule du delta sur la base nette (voir docstring).
    #   net = total_energy_certificates - total_energy_readjustments
    #   delta = (net / enr_ratio) * new_enr_ratio - net
    delta_expression = ExpressionWrapper(
        (((F("total_energy_certificates") - F("total_energy_readjustments")) / F("enr_ratio")) * Value(new_enr_ratio))
        - (F("total_energy_certificates") - F("total_energy_readjustments")),
        output_field=FloatField(),
    )

    # Étape C — Total des réajustements (MWh) pour ce CPO et cette année (sous-requête corrélée).
    readjustments_for_year = (
        ElecCertificateReadjustment.objects.filter(
            cpo_id=OuterRef("cpo_id"),
            year=year,
        )
        .values("cpo_id")
        .annotate(total=Sum("energy_amount"))
        .values("total")[:1]
    )

    # Étape D — Filtre des lignes certificat éligibles, puis agrégation par (cpo_id, nom, année).
    #   - exclusion des sources hors périmètre et des ratios invalides ;
    #   - somme des energy_amount → total_energy_certificates ;
    #   - jointure logique du total des réajustements → total_energy_readjustments ;
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
            total_energy_readjustments=Coalesce(
                Subquery(readjustments_for_year, output_field=FloatField()),
                Value(0.0),
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
