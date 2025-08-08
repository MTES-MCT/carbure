from rest_framework import serializers

from biomethane.models import BiomethaneEntityConfigAmendment


class BiomethaneEntityConfigAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigAmendment
        fields = [
            "id",
            "contract",
            "signature_date",
            "effective_date",
            "amendment_object",
            "amendment_file",
            "amendment_details",
        ]


class BiomethaneEntityConfigAmendmentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigAmendment
        fields = [
            "signature_date",
            "effective_date",
            "amendment_object",
            "amendment_file",
            "amendment_details",
        ]

    amendment_object = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneEntityConfigAmendment.AMENDMENT_OBJECT_CHOICES), required=True
    )

    def to_internal_value(self, data):
        if hasattr(data, "getlist"):
            data = data.copy()
            amendment_objects = data.getlist("amendment_object")
            data.setlist("amendment_object", amendment_objects)
        return super().to_internal_value(data)

    def validate(self, data):
        if BiomethaneEntityConfigAmendment.OTHER in data.get("amendment_object") and not data.get("amendment_details"):
            raise serializers.ValidationError(
                {"amendment_details": ["Ce champ est obligatoire si amendment_object contient 'OTHER'."]}
            )

        return super().validate(data)
