from rest_framework import serializers

from traceability.models import Action


class ConsumptionSerializer(serializers.ModelSerializer):
    type = serializers.HiddenField(default=Action.INIT)

    class Meta:
        model = Action
        fields = [
            "type",
            "pos_id",
            "material",
            "certificate",
            "quantity",
            "site",
            "shipping_date",
            "shipping_distance",
            "shipping_method",
            "working_date",
            "eec",
            "el",
            "ei",
            "ep",
            "etd",
            "eu",
            "eccs",
            "esca",
            "eccr",
        ]
