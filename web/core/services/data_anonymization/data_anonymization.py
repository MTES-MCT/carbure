"""
Data anonymization service for sensitive data in development environments.

Uses bulk_update() and batch processing to optimize performance
when handling large amounts of data.
"""

import time

from django.core.paginator import Paginator
from django.db import transaction
from faker import Faker

from core.services.data_anonymization.delete_carbure_lots import CarbureLotDeleter
from core.services.data_anonymization.delete_orphan_certificates import OrphanCertificateDeleter
from core.services.data_anonymization.truncate_tables import truncate_tables
from core.services.data_anonymization.utils import display_anonymization_summary

# Batch size for processing records in chunks to optimize memory usage
BATCH_SIZE = 1000


class DataAnonymizationService:
    """
    Service for anonymizing sensitive data in the database.

    This service provides a systematic approach to replace sensitive information
    (emails, names, etc.) with anonymized values. It uses bulk_update() to
    optimize performance when processing large datasets.

    The service processes records in batches to avoid memory issues and provides
    optional verbose output to track modifications.
    """

    def __init__(self, verbose=False, batch_size=BATCH_SIZE, dry_run=False, lots_limit=1000):
        """
        Initialize the anonymization service.

        Args:
            verbose: If True, displays detailed modification history for each object.
                     If False, only shows summary statistics.
            batch_size: Number of records to process in each batch (default: 2000)
            dry_run: If True, simulates the anonymization without saving changes to the database.
                     If False, applies the changes to the database.
            lots_limit: Number of lots to keep per year during reduction (default: 1000)
        """
        self.fake = Faker("fr_FR")
        self.batch_size = batch_size
        self.verbose = verbose
        self.dry_run = dry_run
        self.lots_limit = lots_limit

    def _process_anonymizer(self, anonymizer):
        start_time = time.perf_counter()
        queryset = anonymizer.get_queryset()
        updated_fields = anonymizer.get_updated_fields()
        model = anonymizer.get_model()
        model_name = model.__name__

        total = queryset.count()
        if total == 0:
            print(f"   → {model_name}: Aucun enregistrement à traiter")
            return 0, 0.0

        dry_run_indicator = " [DRY-RUN]" if self.dry_run else ""
        print(f"   → {model_name}: {total} enregistrements à traiter...{dry_run_indicator}")

        # Use Paginator to split queryset into manageable batches
        queryset = queryset.order_by("id")
        paginator = Paginator(queryset, self.batch_size)
        total_processed = 0
        # Process each batch
        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            batch = list(page.object_list)
            updated_objects = []
            # Process each object in the current batch
            for object_item in batch:
                updated_object_item = anonymizer.process(object_item)
                if updated_object_item:
                    updated_objects.append(updated_object_item)
            # Save all modifications in bulk for better performance
            # Skip saving if in dry-run mode
            if updated_objects and not self.dry_run:
                with transaction.atomic():
                    model.objects.bulk_update(updated_objects, updated_fields, batch_size=self.batch_size)

            total_processed += len(updated_objects)

        elapsed_time = time.perf_counter() - start_time
        print(f"   → {model_name}: {total_processed} enregistrements traités")
        return total_processed, elapsed_time

    def _delete_data(self):
        """
        Supprime les données excédentaires (lots et certificats orphelins).

        Returns:
            list: Liste des statistiques de suppression
        """
        print("=" * 60)
        print("ÉTAPE 1: Suppression des données")
        print("=" * 60)

        print("Suppression des lots...")
        reducer = CarbureLotDeleter(limit=self.lots_limit, dry_run=self.dry_run)
        _, deleted_lots, lots_elapsed_time = reducer.execute()

        # Suppression des certificats orphelins
        print("Suppression des certificats orphelins...")
        certificate_deleter = OrphanCertificateDeleter(dry_run=self.dry_run)
        deleted_certificates, certificates_elapsed_time = certificate_deleter.delete_orphan_certificates()

        print("Étape 1 terminée\n")

        # Retourner les stats pour le récapitulatif
        return [
            {
                "emoji": "📦",
                "name": "Réduction des lots de carbure",
                "processed": deleted_lots,
                "elapsed_time": lots_elapsed_time,
            },
            {
                "emoji": "📜",
                "name": "Suppression des certificats orphelins",
                "processed": deleted_certificates,
                "elapsed_time": certificates_elapsed_time,
            },
        ]

    def _truncate_tables(self):
        """
        Vide les tables spécifiées (truncate).

        Returns:
            list: Liste vide (pas de stats pour le truncate)
        """
        print("=" * 60)
        print("ÉTAPE 2: Vidage des tables")
        print("=" * 60)
        if not self.dry_run:
            print("Truncate des tables...")
            truncate_tables()
            print("Tables tronquées avec succès")
        else:
            print("[DRY-RUN] Truncate des tables (simulation)")
        print("Étape 2 terminée\n")
        return []

    def _anonymize_data(self):
        """
        Anonymise les données sensibles.

        Returns:
            list: Liste des statistiques d'anonymisation
        """
        print("=" * 60)
        print("ÉTAPE 3: Anonymisation des données")
        print("=" * 60)

        # Define anonymizers with their initialization parameters
        anonymizers_config = [
            # UserAnonymizer(),
            # EntityAnonymizer(self.fake),
            # SiteAnonymizer(self.fake),
            # DepotAnonymizer(self.fake),
            # ProductionSiteAnonymizer(self.fake),
            # BiomethaneContractAnonymizer(self.fake),
            # BiomethaneContractAmendmentAnonymizer(self.fake),
            # BiomethaneInjectionSiteAnonymizer(self.fake),
            # BiomethaneProductionUnitAnonymizer(self.fake),
            # DoubleCountingApplicationAnonymizer(self.fake),
            # DoubleCountingDocFileAnonymizer(self.fake),
            # DoubleCountingSourcingHistoryAnonymizer(self.fake),
            # ElecChargePointAnonymizer(self.fake),
            # ElecMeterAnonymizer(self.fake),
            # ElecTransferCertificateAnonymizer(self.fake),
            # ElecProvisionCertificateAnonymizer(self.fake),
            # ElecProvisionCertificateQualichargeAnonymizer(self.fake),
            # SafTicketAnonymizer(self.fake),
            # SafTicketSourceAnonymizer(self.fake),
            # CarbureLotAnonymizer(self.fake),
            # CertificateAnonymizer(self.fake),
            # CarbureLotCommentAnonymizer(self.fake),
        ]

        # Process each anonymizer and collect statistics
        anonymizer_stats = []
        for anonymizer in anonymizers_config:
            emoji = anonymizer.get_emoji()
            name = anonymizer.get_display_name()
            print(f"{emoji} -------- Anonymisation des {name}...   -------- ")
            processed, elapsed_time = self._process_anonymizer(anonymizer)
            anonymizer_stats.append(
                {
                    "emoji": emoji,
                    "name": name,
                    "processed": processed,
                    "elapsed_time": elapsed_time,
                }
            )
            print(f"{emoji} -------- Fin anonymisation des {name}...   -------- ")

        print("Étape 3 terminée\n")
        return anonymizer_stats

    def anonymize_all(self):
        """
        Main entry point to anonymize all models in the correct order.

        Orchestrates the three main steps: deletion, truncate, and anonymization.
        Displays a summary at the end.
        """
        total_start_time = time.perf_counter()

        # ÉTAPE 1: Vidage des tables
        self._truncate_tables()

        # ÉTAPE 2: Suppression des données
        deletion_stats = self._delete_data()

        # ÉTAPE 3: Anonymisation des données
        anonymizer_stats = self._anonymize_data()

        # Calculer les totaux pour le récapitulatif
        total_elapsed_time = time.perf_counter() - total_start_time
        all_stats = deletion_stats + anonymizer_stats
        total_all_processed = sum(stat["processed"] for stat in all_stats)

        # Afficher le récapitulatif
        display_anonymization_summary(all_stats, total_all_processed, total_elapsed_time)
