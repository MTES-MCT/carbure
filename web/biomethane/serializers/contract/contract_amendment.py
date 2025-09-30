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
        validated_data = super().validate(data)

        if BiomethaneContractAmendment.OTHER in validated_data.get("amendment_object") and not validated_data.get(
            "amendment_details"
        ):
            raise serializers.ValidationError(
                {"amendment_details": [_("Ce champ est obligatoire si amendment_object contient 'OTHER'.")]}
            )

        signature_date = validated_data.get("signature_date")
        effective_date = validated_data.get("effective_date")
        if signature_date and effective_date and effective_date < signature_date:
            raise serializers.ValidationError(
                {"effective_date": [_("La date d'effet doit être postérieure à la date de signature.")]}
            )

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")

        try:
            contract = BiomethaneContract.objects.get(producer=entity)
            validated_data["contract_id"] = contract.id

            # Retirer les valeurs de amendment_object du tableau tracked_amendment_types
            current_tracked_types = set(contract.tracked_amendment_types or [])
            amendment_objects = set(validated_data.get("amendment_object", []))

            # Utiliser la différence d'ensembles pour retirer les éléments
            updated_tracked_types = current_tracked_types - amendment_objects

            # Mettre à jour le contrat avec les nouveaux types trackés
            contract.tracked_amendment_types = list(updated_tracked_types)
            contract.save(update_fields=["tracked_amendment_types"])
        except BiomethaneContract.DoesNotExist:
            raise serializers.ValidationError({"contract": [_("Cette entité n'a pas de contrat associé.")]})

        return super().create(validated_data)
