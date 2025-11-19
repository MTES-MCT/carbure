"""
Fonctions utilitaires pour l'anonymisation des données.

Ces fonctions sont utilisées par les différents anonymiseurs pour
effectuer des opérations communes comme la mise à jour de champs
ou le formatage de l'affichage.
"""

import random


def strikethrough(text):
    """
    Adds Unicode strikethrough characters to text for display purposes.

    This is used to visually show the old value when displaying modifications
    in verbose mode.
    """
    return "\u0336".join(str(text)) + "\u0336"


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
    modifications = {}
    for field_name, new_value in fields_dict.items():
        old_value = getattr(model_instance, field_name, None)
        updated = set_field_if_has_value(model_instance, field_name, new_value)

        if updated:
            modifications[field_name] = (old_value, new_value)
    return model_instance, modifications


def process_object_item(object_item, anonymizer, model_name, verbose):
    updated_object_item, modifications = anonymizer.process(object_item)

    # Display detailed modification history only if verbose mode is enabled
    if modifications and verbose:
        object_id = getattr(object_item, "id", "N/A")
        print(f"\n      [{model_name} #{object_id}]")
        for field_name, (old_value, new_value) in modifications.items():
            old_display = strikethrough(old_value)
            print(f"         {field_name}: {old_display} → {new_value}")

    return updated_object_item


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
