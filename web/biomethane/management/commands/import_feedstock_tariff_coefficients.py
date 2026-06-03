"""
Import feedstock tariff coefficients from Excel.

File: $CARBURE_HOME/web/biomethane/fixtures/import-feedstock-tariff-coefficients.xlsx
Columns: Nom Intrant | Code | Référence AT 2011 | Référence AT 2020/21/23

  python web/manage.py import_feedstock_tariff_coefficients --dry-run=true
  python web/manage.py import_feedstock_tariff_coefficients --dry-run=false
"""

import os
import re

import pandas as pd
from django.core.management.base import BaseCommand

from biomethane.models import BiomethaneFeedstockTariffCoefficient
from core.models import MatierePremiere

Coeff = BiomethaneFeedstockTariffCoefficient

FILENAME = "import-feedstock-tariff-coefficients.xlsx"
COL_CODE = "Code"
COL_AT_2011 = "Référence AT 2011"
COL_AT_2020 = "Référence AT 2020/21/23"


def parse_coefficient(value, allowed):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    text = re.split(r"\s+si\s+", text, maxsplit=1, flags=re.IGNORECASE)[0].strip().upper()
    if text in allowed:
        return text
    raise ValueError(f"invalid coefficient '{value}' (expected one of {allowed})")


class Command(BaseCommand):
    help = "Import coefficients (p1,p2,p3,p,pef) for each feedstock from Excel."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            default="true",
            help="Simulate without writing to the database",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"] == "true"
        carbure_home = os.environ.get("CARBURE_HOME")
        if not carbure_home:
            self.stderr.write("CARBURE_HOME is not set")
            return

        path = os.path.join(carbure_home, "web", "biomethane", "fixtures", FILENAME)
        if not os.path.exists(path):
            self.stderr.write(f"File not found: {path}")
            return

        df = pd.read_excel(path)
        for col in (COL_CODE, COL_AT_2011, COL_AT_2020):
            if col not in df.columns:
                self.stderr.write(f"Missing column: {col}")
                return

        by_code = {mp.code: mp for mp in MatierePremiere.biomethane.all()}

        created = 0
        updated = 0
        errors = 0

        for index, row in df.iterrows():
            code = row[COL_CODE]
            if pd.isna(code) or not str(code).strip():
                self.stderr.write(f"Row {index + 2}: missing code")
                errors += 1
                continue

            code = str(code).strip()
            feedstock = by_code.get(code)
            if not feedstock:
                self.stderr.write(f"Row {index + 2}: feedstock not found: {code}")
                errors += 1
                continue

            for col, regime, allowed in (
                (COL_AT_2011, Coeff.AT_2011, {Coeff.P1, Coeff.P2, Coeff.P3}),
                (COL_AT_2020, Coeff.AT_2020_PLUS, {Coeff.P, Coeff.PEF}),
            ):
                try:
                    coefficient = parse_coefficient(row[col], allowed)
                except ValueError as exc:
                    self.stderr.write(f"Row {index + 2} ({code}): {exc}")
                    errors += 1
                    continue
                if not coefficient:
                    continue

                if dry_run:
                    exists = Coeff.objects.filter(feedstock=feedstock, regime=regime).exists()
                    if exists:
                        updated += 1
                    else:
                        created += 1
                    continue

                _, was_created = Coeff.objects.update_or_create(
                    feedstock=feedstock,
                    regime=regime,
                    defaults={"coefficient": coefficient},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no database changes."))
        if errors:
            self.stderr.write(self.style.ERROR(f"Errors: {errors}"))
        self.stdout.write(
            f"Done. Would create: {created}, would update: {updated}"
            if dry_run
            else f"Done. Created: {created}, updated: {updated}"
        )
