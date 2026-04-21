from importlib.util import find_spec

from django.apps import apps
from django.db.models.fields.related import ForeignObjectRel

EXCLUDED_TRANSLATION_FIELDS = ["id"]


def get_verbose_fields_for_model(model, excluded_fields=None):
    """
    Extract translatable fields from a Django model.

    Keeps only fields that expose an explicit verbose_name and are not listed in
    excluded_fields (defaults to EXCLUDED_TRANSLATION_FIELDS).
    """
    excluded_fields_set = set(excluded_fields or EXCLUDED_TRANSLATION_FIELDS)
    verbose_fields = {}

    for field in model._meta.get_fields():
        if isinstance(field, ForeignObjectRel):
            continue

        field_name = getattr(field, "name", None)
        explicit_verbose_name = getattr(field, "_verbose_name", None)

        if not field_name or explicit_verbose_name is None or field_name in excluded_fields_set:
            continue

        verbose_fields[field_name] = str(explicit_verbose_name)

    return verbose_fields


def get_verbose_fields_by_model_for_module(module_name):
    """
    Return verbose fields grouped by model translation key for one Django app.

    Output shape:
    {
        "<model_key>": {"<field_name>": "<verbose_name>", ...},
        ...
    }
    """
    app_config = _resolve_app_config(module_name)
    if not _has_models_package(app_config.name):
        return {}

    verbose_fields_by_model = {}
    for model in app_config.get_models():
        fields = get_verbose_fields_for_model(model)
        if fields:
            model_key = _get_translation_model_key(model)
            verbose_fields_by_model[model_key] = fields

    return verbose_fields_by_model


def get_verbose_fields_for_translation(module_names):
    """
    Build flat translation keys for one or several Django app modules.

    Output keys follow: <module>.<model>.<field>
    """
    translation_fields = {}

    for module_name in module_names:
        if not module_name:
            continue

        model_fields = get_verbose_fields_by_model_for_module(module_name)
        for model_name, fields in model_fields.items():
            for field_name, verbose_name in fields.items():
                translation_key = f"{module_name}.{model_name}.{field_name}"
                translation_fields[translation_key] = verbose_name

    return translation_fields


def _resolve_app_config(module_name):
    """
    Resolve a Django AppConfig from either app label or full app name.

    Raises LookupError if no matching app is found.
    """
    try:
        return apps.get_app_config(module_name)
    except LookupError:
        for app_config in apps.get_app_configs():
            if app_config.name == module_name:
                return app_config

    raise LookupError(f"Unknown Django app module: {module_name}")


def _has_models_package(module_name):
    """
    Check if a Django app exposes a models package (module.models).
    """
    models_spec = find_spec(f"{module_name}.models")
    return bool(models_spec and models_spec.submodule_search_locations)


def _get_translation_model_key(model):
    """
    Return the model key used in translation keys.

    Priority:
    1. model.translation_model_key (if defined)
    2. model._meta.model_name

    Spaces are replaced with underscores.
    """
    raw_key = getattr(model, "translation_model_key", model._meta.model_name)
    return str(raw_key).replace(" ", "_")
