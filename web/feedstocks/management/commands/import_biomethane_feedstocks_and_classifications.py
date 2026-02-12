import os

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import MatierePremiere
from feedstocks.models import Classification


class Command(BaseCommand):
    """
    Management command to import feedstocks and classifications from XLSX file.
    Use it only once to import the initial feedstocks and classifications for biomethane.

    python web/manage.py import_biomethane_feedstocks_and_classifications
    """

    help = "Import feedstocks and classifications from XLSX file."

    FILENAME = "import-intrants-biomethane.xlsx"

    def handle(self, *args, **options):
        self.flag_existing_matiere_premiere()
        self.stdout.write(self.style.SUCCESS("Existing MatierePremiere flagged as is_displayed=False."))

        filepath = self.get_xlsx_file_path()
        if not filepath:
            return

        self.import_feedstocks_and_classifications(filepath)

    def flag_existing_matiere_premiere(self):
        """Flag existing MatierePremiere as is_biofuel_feedstock=True before importing new ones for biomethane."""
        MatierePremiere.objects.update(is_biofuel_feedstock=True)

    def get_xlsx_file_path(self):
        """Return the path to the XLSX file to import."""
        carbure_home = os.environ.get("CARBURE_HOME")
        if not carbure_home:
            self.stderr.write(self.style.ERROR("CARBURE_HOME environment variable not set"))
            return

        filepath = os.path.join(carbure_home, "web", "feedstocks", "fixtures", self.FILENAME)

        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f"File not found: {filepath}"))
            return

        return filepath

    def import_feedstocks_and_classifications(self, filepath):
        """Import feedstocks and classifications from the XLSX file."""
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read Excel file: {e}"))
            return

        # Check required columns
        required_columns = ["Groupe", "Catégorie", "Sous-catégorie", "Intrant", "Code affichage"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.stderr.write(self.style.ERROR(f"Missing required columns: {', '.join(missing_columns)}"))
            return

        stats = {
            "processed": 0,
            "matiere_premiere_created": 0,
            "matiere_premiere_updated": 0,
            "classification_created": 0,
            "skipped": 0,
            "errors": 0,
        }

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    stats["processed"] += 1

                    # Extract data from row (handle pandas NaN values)
                    groupe = str(row.get("Groupe", "")).strip() if pd.notna(row.get("Groupe")) else ""
                    categorie = str(row.get("Catégorie", "")).strip() if pd.notna(row.get("Catégorie")) else ""
                    sous_categorie = (
                        str(row.get("Sous-catégorie", "")).strip() if pd.notna(row.get("Sous-catégorie")) else ""
                    )
                    intrant = str(row.get("Intrant", "")).strip() if pd.notna(row.get("Intrant")) else ""
                    code_affichage = (
                        str(row.get("Code affichage", "")).strip() if pd.notna(row.get("Code affichage")) else ""
                    )

                    if code_affichage:
                        intrant = code_affichage  # Override intrant with code_affichage if provided

                    if not intrant:
                        self.stdout.write(self.style.WARNING(f"Row {index + 1}: Missing 'Intrant', skipping"))
                        stats["skipped"] += 1
                        continue

                    self.stdout.write(f"\nProcessing row {index + 1}: {intrant}")

                    # 1. Get or create Classification
                    classification, class_created = Classification.objects.get_or_create(
                        group=groupe,
                        category=categorie,
                        subcategory=sous_categorie,
                    )

                    if class_created:
                        self.stdout.write(
                            self.style.SUCCESS(f"  - Created Classification: {groupe} / {categorie} / {sous_categorie}")
                        )
                        stats["classification_created"] += 1
                    else:
                        self.stdout.write(f"  - Found existing Classification: {groupe} / {categorie} / {sous_categorie}")

                    # 2. Update or create MatierePremiere and update is_methanogenic
                    try:
                        matiere_premiere = MatierePremiere.objects.get(name=intrant, classification=classification)
                        # Update is_methanogenic if not already set
                        if not matiere_premiere.is_methanogenic:
                            matiere_premiere.is_methanogenic = True
                            matiere_premiere.save()
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  - Updated MatierePremiere: {matiere_premiere.name} " f"(is_methanogenic=True)"
                                )
                            )
                            stats["matiere_premiere_updated"] += 1
                        else:
                            self.stdout.write(f"  - Found existing MatierePremiere: {matiere_premiere.name}")
                    except MatierePremiere.DoesNotExist:
                        # Create new MatierePremiere
                        matiere_premiere = MatierePremiere.biofuel.create(
                            name=intrant[:256],
                            name_en=intrant[:256],
                            code=f"{intrant.upper().replace(' ', '_')[:60]}_{index}",
                            is_methanogenic=True,
                            classification=classification,
                            description="",
                        )
                        self.stdout.write(self.style.SUCCESS(f"  - Created MatierePremiere: {matiere_premiere.name}"))
                        stats["matiere_premiere_created"] += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Row {index + 1}: Error processing row: {e}"))
                    stats["errors"] += 1
                    continue

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Processed: {stats['processed']} rows"))
        self.stdout.write(self.style.SUCCESS(f"MatierePremiere created: {stats['matiere_premiere_created']}"))
        self.stdout.write(self.style.SUCCESS(f"MatierePremiere updated: {stats['matiere_premiere_updated']}"))
        self.stdout.write(self.style.SUCCESS(f"Classification created: {stats['classification_created']}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {stats['skipped']} rows"))
        self.stdout.write(self.style.ERROR(f"Errors: {stats['errors']} rows"))
        self.stdout.write(self.style.SUCCESS("\nAll changes saved to database"))
