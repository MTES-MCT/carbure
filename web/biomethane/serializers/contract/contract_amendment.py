from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneContract, BiomethaneContractAmendment


class BaseBiomethaneContractAmendmentSerializer(serializers.ModelSerializer):
    amendment_object = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneContractAmendment.AMENDMENT_OBJECT_CHOICES), required=True
    )

    class Meta:
        model = BiomethaneContractAmendment
        exclude = ["contract"]

    def to_internal_value(self, data):
        if hasattr(data, "getlist"):
            data = data.copy()
            amendment_objects = data.getlist("amendment_object")
            data.setlist("amendment_object", amendment_objects)
        return super().to_internal_value(data)


class BiomethaneContractAmendmentSerializer(BaseBiomethaneContractAmendmentSerializer):
    class Meta(BaseBiomethaneContractAmendmentSerializer.Meta):
        exclude = []


class BiomethaneContractAmendmentAddSerializer(BaseBiomethaneContractAmendmentSerializer):
    def validate(self, data):
        if BiomethaneContractAmendment.OTHER in data.get("amendment_object") and not data.get("amendment_details"):
            raise serializers.ValidationError(
                {"amendment_details": [_("Ce champ est obligatoire si amendment_object contient 'OTHER'.")]}
            )
        return super().validate(data)

    def create(self, validated_data):
        entity = self.context.get("entity")

        try:
            contract = BiomethaneContract.objects.get(producer=entity)
            validated_data["contract_id"] = contract.id
        except BiomethaneContract.DoesNotExist:
            raise serializers.ValidationError({"contract": [_("Cette entité n'a pas de contrat associé.")]})

        return super().create(validated_data)
