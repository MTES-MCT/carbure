"""
Commande Django management pour anonymiser les données sensibles.

Usage:
    python manage.py anonymize_data --dry-run
    python manage.py anonymize_data --seed 42
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from core.services.data_anonymization import DataAnonymizationService


class Command(BaseCommand):
    help = "Anonymise les données sensibles de la base de données pour les environnements de développement"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=2000,
            help="Taille des batches pour le traitement (défaut: 2000)",
        )

    def handle(self, *args, **options):
        # Vérification de sécurité
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR("⚠️  ATTENTION: Cette commande ne doit être exécutée qu'en environnement de développement!")
            )
            response = input("Êtes-vous sûr de vouloir continuer? (oui/non): ")
            if response.lower() != "oui":
                self.stdout.write(self.style.WARNING("Opération annulée"))
                return

        # Créer le service
        service = DataAnonymizationService(batch_size=options["batch_size"])

        # Exécuter l'anonymisation
        try:
            service.anonymize_all()
            self.stdout.write(self.style.SUCCESS("\n✅ Anonymisation terminée avec succès!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Erreur lors de l'anonymisation: {e}"))
            import traceback

            traceback.print_exc()
            raise
