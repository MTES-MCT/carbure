from rest_framework import serializers

from biomethane.models import BiomethaneContract
from biomethane.models.biomethane_contract_amendment import BiomethaneContractAmendment
from biomethane.serializers.contract.contract_amendment import BiomethaneContractAmendmentSerializer
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.services.contract import BiomethaneContractService
from core.serializers import check_fields_required


class BiomethaneContractSerializer(serializers.ModelSerializer):
    amendments = BiomethaneContractAmendmentSerializer(many=True, read_only=True)
    tracked_amendment_types = serializers.ListField(
        child=serializers.ChoiceField(choices=BiomethaneContractAmendment.TRACKED_AMENDMENT_TYPES), read_only=True
    )

    class Meta:
        model = BiomethaneContract
        fields = "__all__"


class BiomethaneContractInputSerializer(serializers.ModelSerializer):
    # Allow null to distinguish between False and not provided
    cmax_annualized = serializers.BooleanField(allow_null=True, required=False)

    # Allow the biomethane producer to set/unset the RED II status if the cmax or pap_contracted
    # is lower than the threshold (see biomethane contract model)
    is_red_ii = serializers.BooleanField(required=False)

    class Meta:
        model = BiomethaneContract
        exclude = ["producer"]

    def validate(self, data):
        validated_data = super().validate(data)
        contract = self.instance

        # Use the service to validate the contract data and get required fields
        errors, required_fields = BiomethaneContractService.validate_contract(contract, validated_data)

        # Check for validation errors
        check_fields_required(validated_data, required_fields)

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["producer"] = entity
        BiomethaneContractService.handle_is_red_ii(validated_data, entity)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        BiomethaneContractService.handle_is_red_ii(validated_data, instance.producer)

        tracked_types = BiomethaneContractService.get_tracked_amendment_types(instance, validated_data)
        validated_data["tracked_amendment_types"] = tracked_types

        # Check if annual declaration needs to be reset
        if BiomethaneAnnualDeclarationService.has_watched_field_changed(instance, validated_data.keys()):
            BiomethaneAnnualDeclarationService.reset_annual_declaration_status(instance.producer)

        return super().update(instance, validated_data)
