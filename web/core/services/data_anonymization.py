"""
Data anonymization service for sensitive data in development environments.

Uses bulk_update() and batch processing to optimize performance
when handling large amounts of data.
"""

from django.core.paginator import Paginator
from django.db import transaction
from faker import Faker

from core.services.data_anonymization.carbure_lot_comments import CarbureLotCommentAnonymizer
from core.services.data_anonymization.certificates import CertificateAnonymizer
from core.services.data_anonymization.utils import process_object_item

# Batch size for processing records in chunks to optimize memory usage
BATCH_SIZE = 3000


class DataAnonymizationService:
    """
    Service for anonymizing sensitive data in the database.

    This service provides a systematic approach to replace sensitive information
    (emails, names, etc.) with anonymized values. It uses bulk_update() to
    optimize performance when processing large datasets.

    The service processes records in batches to avoid memory issues and provides
    optional verbose output to track modifications.
    """

    def __init__(self, verbose=False, batch_size=BATCH_SIZE, dry_run=False):
        """
        Initialize the anonymization service.

        Args:
            verbose: If True, displays detailed modification history for each object.
                     If False, only shows summary statistics.
            batch_size: Number of records to process in each batch (default: 2000)
            dry_run: If True, simulates the anonymization without saving changes to the database.
                     If False, applies the changes to the database.
        """
        self.fake = Faker("fr_FR")
        self.batch_size = batch_size
        self.verbose = verbose
        self.dry_run = dry_run

    def _process_anonymizer(self, anonymizer):
        queryset = anonymizer.get_queryset()
        updated_fields = anonymizer.get_updated_fields()
        model = anonymizer.get_model()
        model_name = model.__name__

        total = queryset.count()
        if total == 0:
            print(f"   → {model_name}: Aucun enregistrement à traiter")
            return 0

        dry_run_indicator = " [DRY-RUN]" if self.dry_run else ""
        print(f"   → {model_name}: {total} enregistrements à traiter...{dry_run_indicator}")

        # Use Paginator to split queryset into manageable batches
        paginator = Paginator(queryset, self.batch_size)
        total_processed = 0

        # Process each batch
        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            batch = list(page.object_list)
            updated_objects = []

            # Process each object in the current batch
            for object_item in batch:
                updated_object_item = process_object_item(object_item, anonymizer, model_name, self.verbose)
                if updated_object_item:
                    updated_objects.append(updated_object_item)

            # Save all modifications in bulk for better performance
            # Skip saving if in dry-run mode
            if updated_objects and not self.dry_run:
                model.objects.bulk_update(updated_objects, updated_fields, batch_size=self.batch_size)

            total_processed += len(updated_objects)

        print(f"   → {model_name}: {total_processed} enregistrements traités")
        return total_processed

    def anonymize_all(self):
        """
        Main entry point to anonymize all models in the correct order.

        Uses transaction.atomic() only when not in dry-run mode to avoid
        unnecessary database transactions during simulation.
        """
        if self.dry_run:
            # In dry-run mode, don't use transactions since we're not saving anything
            self._anonymize_all_internal()
        else:
            # In normal mode, use transaction for data integrity
            with transaction.atomic():
                self._anonymize_all_internal()

    def _anonymize_all_internal(self):
        """
        Internal method that executes anonymization methods in the correct order.
        """
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
            CertificateAnonymizer(self.fake),
            CarbureLotCommentAnonymizer(self.fake),
        ]

        # Process each anonymizer
        for anonymizer in anonymizers_config:
            emoji = anonymizer.get_emoji()
            name = anonymizer.get_display_name()
            print(f"{emoji} -------- Anonymisation des {name}...   -------- ")
            self._process_anonymizer(anonymizer)
            print(f"{emoji} -------- Fin anonymisation des {name}...   -------- ")
