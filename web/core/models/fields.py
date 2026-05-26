from django.core.exceptions import ValidationError
from django.db import models


class JSONChoiceField(models.JSONField):
    """
    JSON field constrained by choices and storing a list of keys.
    """

    default_error_messages = {
        "not_a_list": "La valeur doit être une liste.",
        "invalid_choice": "Valeur(s) invalide(s) : %(values)s",
    }

    def validate(self, value, model_instance):
        # Run base JSONField validation without Field's built-in choices check.
        # Field.validate expects scalar values for choices and is not suitable for JSON lists.
        original_choices = self.choices
        self.choices = None
        try:
            super().validate(value, model_instance)
        finally:
            self.choices = original_choices

        if value is None or not self.choices:
            return

        allowed_values = {choice_value for choice_value, _ in self.flatchoices}

        if not isinstance(value, list):
            raise ValidationError(self.error_messages["not_a_list"])

        invalid_values = [item for item in value if item not in allowed_values]
        if invalid_values:
            raise ValidationError(
                self.error_messages["invalid_choice"],
                params={"values": ", ".join(str(v) for v in invalid_values)},
            )

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)

        if not self.choices:
            return

        def get_field_display(instance):
            raw_value = getattr(instance, self.attname)
            labels = self.get_labels(raw_value)
            if isinstance(labels, list):
                return ", ".join(str(label) for label in labels)
            return labels

        setattr(cls, f"get_{self.name}_display", get_field_display)

    def get_choice_label(self, value):
        return dict(self.flatchoices).get(value, value)

    def get_labels(self, value):
        if isinstance(value, list):
            return [self.get_choice_label(item) for item in value]
        return self.get_choice_label(value)
