"""
Data anonymization service for sensitive data in development environments.

Uses bulk_update() and batch processing to optimize performance
when handling large amounts of data.
"""

import time

from faker import Faker

from anonymization.services.update_certificate_id import update_certificate_ids

from .anonymizers.biomethane.contract_amendments import BiomethaneContractAmendmentAnonymizer
from .anonymizers.biomethane.contracts import BiomethaneContractAnonymizer
from .anonymizers.biomethane.injection_sites import BiomethaneInjectionSiteAnonymizer
from .anonymizers.biomethane.production_units import BiomethaneProductionUnitAnonymizer
from .anonymizers.carbure_lot_comments import CarbureLotCommentAnonymizer
from .anonymizers.carbure_lots import CarbureLotAnonymizer
from .anonymizers.certificates import CertificateAnonymizer
from .anonymizers.depots import DepotAnonymizer
from .anonymizers.double_counting.applications import DoubleCountingApplicationAnonymizer
from .anonymizers.double_counting.doc_files import DoubleCountingDocFileAnonymizer
from .anonymizers.double_counting.registrations import DoubleCountingRegistrationAnonymizer
from .anonymizers.double_counting.sourcing_history import DoubleCountingSourcingHistoryAnonymizer
from .anonymizers.elec.charge_points import ElecChargePointAnonymizer
from .anonymizers.elec.meters import ElecMeterAnonymizer
from .anonymizers.elec.provision_certificates import ElecProvisionCertificateAnonymizer
from .anonymizers.elec.provision_certificates_qualicharge import (
    ElecProvisionCertificateQualichargeAnonymizer,
)
from .anonymizers.elec.transfer_certificates import ElecTransferCertificateAnonymizer
from .anonymizers.entities import EntityAnonymizer
from .anonymizers.saf.ticket_sources import SafTicketSourceAnonymizer
from .anonymizers.saf.tickets import SafTicketAnonymizer
from .anonymizers.sites import SiteAnonymizer
from .anonymizers.users import UserAnonymizer
from .deleters.delete_carbure_lots import CarbureLotDeleter
from .deleters.delete_empty_operations import EmptyOperationDeleter
from .deleters.delete_orphan_certificates import OrphanCertificateDeleter
from .truncate_tables import truncate_tables
from .utils import display_anonymization_summary, process_queryset_in_batches

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

        total_processed = process_queryset_in_batches(
            queryset=queryset,
            process_func=anonymizer.process,
            batch_size=self.batch_size,
            dry_run=self.dry_run,
            model=model,
            updated_fields=updated_fields,
        )

        elapsed_time = time.perf_counter() - start_time
        print(f"   → {model_name}: {total_processed} enregistrements traités")
        return total_processed, elapsed_time

    def _delete_data(self):
        print("=" * 60)
        print("ÉTAPE 2: Suppression des données")
        print("=" * 60)

        print("Suppression des lots...")
        deleter = CarbureLotDeleter(limit=self.lots_limit, dry_run=self.dry_run)
        _, deleted_lots, lots_elapsed_time = deleter.execute()

        print("Suppression des certificats orphelins...")
        certificate_deleter = OrphanCertificateDeleter(dry_run=self.dry_run)
        deleted_certificates, certificates_elapsed_time = certificate_deleter.delete_orphan_certificates()

        print("Suppression des opérations vides...")
        operation_deleter = EmptyOperationDeleter(dry_run=self.dry_run)
        deleted_operations, operations_elapsed_time = operation_deleter.delete_empty_operations()

        print("Étape 2 terminée\n")

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
            {
                "emoji": "⚙️",
                "name": "Suppression des opérations vides",
                "processed": deleted_operations,
                "elapsed_time": operations_elapsed_time,
            },
        ]

    def _truncate_tables(self):
        print("=" * 60)
        print("ÉTAPE 1: Vidage des tables")
        print("=" * 60)
        if not self.dry_run:
            print("Truncate des tables...")
            truncate_tables()
            print("Tables tronquées avec succès")
        else:
            print("[DRY-RUN] Truncate des tables (simulation)")
        print("Étape 1 terminée\n")
        return []

    def _anonymize_data(self):
        print("=" * 60)
        print("ÉTAPE 3: Anonymisation des données")
        print("=" * 60)

        anonymizers_config = [
            UserAnonymizer(),
            EntityAnonymizer(self.fake),
            SiteAnonymizer(self.fake),
            DepotAnonymizer(self.fake),
            BiomethaneContractAnonymizer(self.fake),
            BiomethaneContractAmendmentAnonymizer(self.fake),
            BiomethaneInjectionSiteAnonymizer(self.fake),
            BiomethaneProductionUnitAnonymizer(self.fake),
            DoubleCountingApplicationAnonymizer(self.fake),
            DoubleCountingDocFileAnonymizer(self.fake),
            DoubleCountingSourcingHistoryAnonymizer(self.fake),
            ElecChargePointAnonymizer(self.fake),
            ElecMeterAnonymizer(self.fake),
            ElecTransferCertificateAnonymizer(self.fake),
            ElecProvisionCertificateAnonymizer(self.fake),
            ElecProvisionCertificateQualichargeAnonymizer(self.fake),
            SafTicketAnonymizer(self.fake),
            SafTicketSourceAnonymizer(self.fake),
            CarbureLotAnonymizer(self.fake),
            DoubleCountingRegistrationAnonymizer(self.fake),
            CertificateAnonymizer(self.fake),
            CarbureLotCommentAnonymizer(self.fake),
        ]

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

        self._truncate_tables()
        deletion_stats = self._delete_data()
        anonymizer_stats = self._anonymize_data()
        rows_updated = update_certificate_ids(dry_run=self.dry_run)

        total_elapsed_time = time.perf_counter() - total_start_time
        all_stats = deletion_stats + anonymizer_stats
        total_all_processed = sum(stat["processed"] for stat in all_stats) + rows_updated

        display_anonymization_summary(all_stats, total_all_processed, total_elapsed_time)
