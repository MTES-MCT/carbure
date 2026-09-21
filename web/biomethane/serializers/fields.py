from rest_framework import serializers


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
