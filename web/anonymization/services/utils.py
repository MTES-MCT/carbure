"""
Fonctions utilitaires pour l'anonymisation des données.

Ces fonctions sont utilisées par les différents anonymiseurs pour
effectuer des opérations communes comme la mise à jour de champs
ou le formatage de l'affichage.
"""

import random

from django.db import transaction


def set_field_if_has_value(model_instance, field_name, new_value):
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


def anonymize_fields_and_collect_modifications(model_instance, fields_dict):
    """
    Updates multiple fields on a model instance and tracks modifications.

    This method attempts to update all specified fields and returns a dictionary
    of all modifications made (old value -> new value pairs).
    """
    for field_name, new_value in fields_dict.items():
        set_field_if_has_value(model_instance, field_name, new_value)

    return model_instance


def get_french_coordinates():
    return f"{42 + random.uniform(0, 9):.6f}, {random.uniform(-5, 10):.6f}"


def format_duration(seconds):
    """Format duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.2f}s"


def process_queryset_in_batches(queryset, process_func, batch_size, dry_run=False, model=None, updated_fields=None):
    """
    Process objects from a queryset in batches using an iterator to avoid memory issues.

    This function processes the queryset in chunks, applying a processing function
    to each object and then bulk updating them in batches to prevent memory problems.

    Args:
        queryset: Django QuerySet of objects to process
        process_func: Function to apply to each object (should return the updated object or None)
        batch_size: Number of objects to process per batch
        dry_run: If True, simulates processing without saving changes to the database
        model: Model class (required if not in dry_run mode)
        updated_fields: List of field names to update (required if not in dry_run mode)

    Returns:
        int: Total number of objects processed
    """
    total_to_process = queryset.count()
    if total_to_process == 0:
        return 0

    queryset = queryset.order_by("id")
    total_processed = 0
    updated_objects = []
    processed_count = 0

    # Use iterator to process queryset in chunks without loading everything into memory
    for obj in queryset.iterator(chunk_size=batch_size):
        updated_obj = process_func(obj)
        if updated_obj:
            updated_objects.append(updated_obj)
        processed_count += 1

        # Process batch when size is reached or when we've processed all items
        if len(updated_objects) >= batch_size or processed_count >= total_to_process:
            if updated_objects and not dry_run:
                with transaction.atomic():
                    model.objects.bulk_update(updated_objects, updated_fields, batch_size=batch_size)
            total_processed += len(updated_objects)
            updated_objects = []

    return total_processed


def delete_queryset_in_batches(queryset, batch_size, dry_run=False, item_name="objets"):
    """
    Delete objects from a queryset in batches using an iterator to avoid memory issues.

    This function processes the queryset in chunks, deleting objects in batches
    to prevent memory problems and database lock issues.

    Args:
        queryset: Django QuerySet of objects to delete
        batch_size: Number of objects to delete per batch
        dry_run: If True, simulates deletion without modifying data
        item_name: Name of the items being deleted (for display messages, e.g., "lots", "certificats")

    Returns:
        int: Total number of objects deleted (or that would be deleted in dry_run mode)
    """
    total_to_delete = queryset.count()
    if total_to_delete == 0:
        return 0

    if dry_run:
        num_batches = ((total_to_delete - 1) // batch_size) + 1
        print(f"       [DRY-RUN] {total_to_delete} {item_name} seraient supprimés en {num_batches} batch(s)")
        return total_to_delete

    model = queryset.model
    total_deleted = 0
    total_batches = ((total_to_delete - 1) // batch_size) + 1

    print(f"       Suppression de {total_to_delete} {item_name} en {total_batches} batch(s)...")

    # Use iterator to process queryset in chunks without loading everything into memory
    batch_ids = []
    batch_num = 0
    processed_count = 0

    for obj in queryset.iterator(chunk_size=batch_size):
        batch_ids.append(obj.id)
        processed_count += 1

        # Process batch when size is reached or when we've processed all items
        if len(batch_ids) >= batch_size or processed_count >= total_to_delete:
            batch_num += 1
            with transaction.atomic():
                deleted = model.objects.filter(id__in=batch_ids).delete()
                # deleted[1] is a dict mapping model labels to counts
                # Use model._meta.label which gives the full label (app_label.model_name)
                deleted_count = deleted[1].get(model._meta.label, deleted[0])

                print(
                    f"         Batch {batch_num}/{total_batches}: {deleted_count} {item_name} supprimés "
                    f"(sur {len(batch_ids)} attendus)"
                )
                total_deleted += deleted_count
            batch_ids = []

    print(f"       Total supprimé: {total_deleted} {item_name} (sur {total_to_delete} attendus)")
    return total_deleted


def display_anonymization_summary(anonymizer_stats, total_processed, total_elapsed_time):
    """
    Display a summary table of anonymization statistics.

    Args:
        anonymizer_stats: List of dictionaries containing anonymizer statistics.
                         Each dict should have: emoji, name, processed, elapsed_time
        total_processed: Total number of records processed across all anonymizers
        total_elapsed_time: Total elapsed time in seconds
    """
    print(f"\n{'='*70}")
    print("📊 RÉCAPITULATIF DE L'ANONYMISATION")
    print(f"{'='*70}")
    for stat in anonymizer_stats:
        if stat["processed"] > 0:
            formatted_time = format_duration(stat["elapsed_time"])
            print(f"{stat['emoji']} {stat['name']:.<50} {stat['processed']:>8} enregistrements  {formatted_time:>12}")
    print(f"{'-'*70}")
    formatted_total_time = format_duration(total_elapsed_time)
    print(f"{'TOTAL':.<50} {total_processed:>8} enregistrements  {formatted_total_time:>12}")
    print(f"{'='*70}")
