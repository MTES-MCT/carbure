"""
Commande Django management pour anonymiser les données sensibles.

"""

import os

from django.core.management.base import BaseCommand

from core.services.data_anonymization import BATCH_SIZE, DataAnonymizationService


class Command(BaseCommand):
    help = "Anonymise les données sensibles de la base de données pour les environnements de développement"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=BATCH_SIZE,
            help="Taille des batches pour le traitement (défaut: 2000)",
        )
        parser.add_argument(
            "--verbose",
            default=False,
            action="store_true",
            help="Affiche les modifications en détail",
        )
        parser.add_argument(
            "--dry-run",
            default=False,
            action="store_true",
            help="Simule l'anonymisation sans modifier les données (mode test)",
        )
        parser.add_argument(
            "--force",
            default=False,
            action="store_true",
            help="Force l'anonymisation sans confirmation",
        )
        parser.add_argument(
            "--lots-limit",
            type=int,
            default=1000,
            help="Nombre de lots à garder par année lors de la réduction (défaut: 1000)",
        )

    def handle(self, *args, **options):
        env = os.environ["IMAGE_TAG"]

        if env not in ["dev", "local"]:
            self.stdout.write(
                self.style.ERROR("⚠️  ATTENTION: Cette commande ne doit être exécutée qu'en environnement de développement!")
            )
            return

        if not options["dry_run"] and not options["force"]:
            self.stdout.write(self.style.ERROR("⚠️  ATTENTION: Vous allez modifier toute la base de données."))
            response = input("Êtes-vous sûr de vouloir continuer? (oui/non): ")
            if response.lower() != "oui":
                self.stdout.write(self.style.WARNING("Opération annulée"))
                return

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING("\n🔍 MODE DRY-RUN: Aucune modification ne sera appliquée à la base de données\n")
            )

        service = DataAnonymizationService(
            batch_size=options["batch_size"],
            verbose=options["verbose"],
            dry_run=options["dry_run"],
            lots_limit=options["lots_limit"],
        )

        try:
            service.anonymize_all()
            if options["dry_run"]:
                self.stdout.write(
                    self.style.SUCCESS("\n✅ Simulation terminée avec succès! (Aucune modification appliquée)")
                )
            else:
                self.stdout.write(self.style.SUCCESS("\n✅ Anonymisation terminée avec succès!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Erreur lors de l'anonymisation: {e}"))
            import traceback

            traceback.print_exc()
            raise
