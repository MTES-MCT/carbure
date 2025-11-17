"""
Data anonymization service for sensitive data in development environments.

Uses bulk_update() and batch processing to optimize performance
when handling large amounts of data.
"""

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import transaction
from faker import Faker

User = get_user_model()

# Batch size for processing records in chunks to optimize memory usage
BATCH_SIZE = 2000


def _strikethrough(text):
    """
    Adds Unicode strikethrough characters to text for display purposes.

    This is used to visually show the old value when displaying modifications
    in verbose mode.
    """
    return "\u0336".join(str(text)) + "\u0336"


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

    def _update_field_if_exists(self, model_instance, field_name, new_value):
        """
        Updates a field on a model instance if it exists and has a value.

        This method checks if the field exists and is not empty before updating it.
        This prevents overwriting None or empty values unnecessarily.
        """
        current_value = getattr(model_instance, field_name, None)

        if current_value is not None and current_value != "":
            setattr(model_instance, field_name, new_value)
            return True

        return False

    def _update_fields_if_exist(self, model_instance, fields_dict):
        """
        Updates multiple fields on a model instance and tracks modifications.

        This method attempts to update all specified fields and returns a dictionary
        of all modifications made (old value -> new value pairs).
        """
        modifications = {}
        for field_name, new_value in fields_dict.items():
            old_value = getattr(model_instance, field_name, None)
            updated = self._update_field_if_exists(model_instance, field_name, new_value)

            if updated:
                modifications[field_name] = (old_value, new_value)
        return modifications

    def _process_in_batches(self, queryset, process_model_object, updated_fields, model_name):
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
                updated_object_item, modifications = process_model_object(object_item)
                if updated_object_item:
                    updated_objects.append(updated_object_item)

                    # Display detailed modification history only if verbose mode is enabled
                    if modifications and self.verbose:
                        object_id = getattr(object_item, "id", "N/A")
                        print(f"\n      [{model_name} #{object_id}]")
                        for field_name, (old_value, new_value) in modifications.items():
                            old_display = _strikethrough(old_value)
                            print(f"         {field_name}: {old_display} → {new_value}")

            # Save all modifications in bulk for better performance
            # Skip saving if in dry-run mode
            if updated_objects and not self.dry_run:
                type(updated_objects[0]).objects.bulk_update(updated_objects, updated_fields, batch_size=self.batch_size)

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
        # Execute anonymization methods in the correct order
        # Order matters: anonymize dependent models first if needed
        self.anonymize_users()

    def anonymize_users(self):
        print("📝 Anonymisation des utilisateurs...")

        def process_user(user):
            modifications = self._update_fields_if_exist(
                user,
                {
                    "email": f"user{user.id}@anonymized.local",
                    "name": f"Utilisateur {user.id}",
                },
            )
            return user, modifications

        self._process_in_batches(User.objects.all(), process_user, ["email", "name"], "Users")
