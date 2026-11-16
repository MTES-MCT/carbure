from traceability.serializers.creation import ActionCreationSerializer


class ConsumptionSerializer(ActionCreationSerializer):
    class Meta(ActionCreationSerializer.Meta):
        fields = [
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
