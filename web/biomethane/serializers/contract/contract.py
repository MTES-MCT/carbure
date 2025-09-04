from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneContract
from biomethane.serializers.contract.contract_amendment import BiomethaneContractAmendmentSerializer


class BiomethaneContractSerializer(serializers.ModelSerializer):
    amendments = BiomethaneContractAmendmentSerializer(many=True, read_only=True)

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
        errors = {}
        required_fields = []
        contract = self.instance

        contract_fields = [
            "signature_date",
            "effective_date",
            "general_conditions_file",
            "specific_conditions_file",
        ]

        # If the contract document already exists (signed), these fields cannot be updated
        if contract and contract.does_contract_exist():
            not_updatable_fields = [field for field in contract_fields if field in validated_data]
            for field in not_updatable_fields:
                errors[field] = [_(f"Le champ {field} ne peut pas être modifié une fois le contrat signé.")]
        else:
            # If the contract does not exist, check if any of the contract fields are provided
            for field in contract_fields:
                if field in validated_data:
                    # Then all contract fields become required
                    required_fields += contract_fields
                    continue

        tariff_reference = validated_data.get("tariff_reference")

        # Tariff rule 1
        if tariff_reference in BiomethaneContract.TARIFF_RULE_1:
            required_fields += ["cmax", "cmax_annualized", "installation_category"]

            cmax_annualized = validated_data.get("cmax_annualized")
            cmax_annualized_value = validated_data.get("cmax_annualized_value")

            if cmax_annualized and not cmax_annualized_value:
                errors["cmax_annualized_value"] = [
                    _("Le champ cmax_annualized_value est obligatoire si cmax_annualized est vrai.")
                ]

        # Tariff rule 2
        elif tariff_reference in BiomethaneContract.TARIFF_RULE_2:
            required_fields.append("pap_contracted")

        for field in required_fields:
            if validated_data.get(field) in [None, ""]:
                errors[field] = [_("Ce champ est obligatoire.")]

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["producer"] = entity
        return super().create(validated_data)

    def update(self, instance, validated_data):
        is_red_ii = validated_data.get("is_red_ii")
        cmax = validated_data.get("cmax")
        pap_contracted = validated_data.get("pap_contracted")

        # If cmax or pap_contracted is below the threshold and
        # the user does not want to be subject to RED II, then is_red_ii is set to False
        if is_red_ii is False and ((cmax and cmax <= 200) or (pap_contracted and pap_contracted <= 19.5)):
            instance.producer.is_red_ii = is_red_ii
            instance.producer.save(update_fields=["is_red_ii"])

        return super().update(instance, validated_data)
