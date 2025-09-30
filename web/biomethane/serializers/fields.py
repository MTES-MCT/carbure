from rest_framework import serializers


class LabelChoiceField(serializers.ChoiceField):
    """
    Choice field that accepts both values and labels from Django model choices
    """

    def __init__(self, choices=(), **kwargs):
        super().__init__(choices=choices, **kwargs)
        # Create reverse mapping: label -> value
        self.label_to_value = {label.lower(): value for value, label in choices}
        # Also accept original values
        self.label_to_value.update({value: value for value, label in choices})

    def to_internal_value(self, data):
        # Convert label to value if needed
        if data.lower() in self.label_to_value:
            data = self.label_to_value[data.lower()]
        return super().to_internal_value(data)


class EuropeanFloatField(serializers.FloatField):
    """
    Float field that accepts both European (comma) and American (dot) decimal notation
    """

    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.replace(",", ".")
        return super().to_internal_value(data)


class DepartmentField(serializers.CharField):
    """
    Field that handles department 'code - name' and converts to department code
    """

    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.split(" - ")[0].strip()
        return super().to_internal_value(data)
