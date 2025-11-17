"""
Fonctions utilitaires pour l'anonymisation des données.

Ces fonctions sont utilisées par les différents anonymiseurs pour
effectuer des opérations communes comme la mise à jour de champs
ou le formatage de l'affichage.
"""


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
