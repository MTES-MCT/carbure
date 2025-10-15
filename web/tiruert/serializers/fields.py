from rest_framework import serializers


class RoundedFloatField(serializers.FloatField):
    """FloatField that rounds the value to a specified number of decimal places."""

    def __init__(self, decimal_places=2, **kwargs):
        self.decimal_places = decimal_places
        super().__init__(**kwargs)

    def to_representation(self, value):
        if value is None:
            return None
        return round(float(value), self.decimal_places)
