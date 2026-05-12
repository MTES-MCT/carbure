from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneContract, BiomethaneContractAmendment
from core.serializers import check_fields_required
from core.utils import check_file_size_and_extension


class BaseBiomethaneContractAmendmentSerializer(serializers.ModelSerializer):
    amendment_object = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneContractAmendment.AMENDMENT_OBJECT_CHOICES), required=True
    )

    class Meta:
        model = BiomethaneContractAmendment
        exclude = ["contract"]


class BiomethaneContractAmendmentSerializer(BaseBiomethaneContractAmendmentSerializer):
    class Meta(BaseBiomethaneContractAmendmentSerializer.Meta):
        exclude = []


class BiomethaneContractAmendmentAddSerializer(BaseBiomethaneContractAmendmentSerializer):
    def validate(self, data):
        validated_data = super().validate(data)

        # Check file size and extension
        if validated_data.get("amendment_file"):
            check_file_size_and_extension(
                validated_data["amendment_file"],
                max_size_mb=10,
                extensions=[".pdf", ".doc", ".docx", ".zip"],
            )

        if BiomethaneContractAmendment.OTHER in validated_data.get("amendment_object"):
            check_fields_required(validated_data, ["amendment_details"])

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
