from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneContract
from biomethane.serializers import BiomethaneContractAmendmentSerializer


class BiomethaneContractSerializer(serializers.ModelSerializer):
    amendments = BiomethaneContractAmendmentSerializer(many=True, read_only=True)

    class Meta:
        model = BiomethaneContract
        fields = [
            "tariff_reference",
            "buyer",
            "installation_category",
            "cmax",
            "cmax_annualized",
            "cmax_annualized_value",
            "pap_contracted",
            "signature_date",
            "effective_date",
            "general_conditions_file",
            "specific_conditions_file",
            "amendments",
            "producer",
        ]


def handle_fields_requirement(data, required_fields=None, errors=None, instance=None):
    required_fields = required_fields or []
    errors = errors or {}

    tariff_reference = data.get("tariff_reference")

    # If existing instance (PATCH method), use its tariff_reference if not provided
    if tariff_reference is None and instance:
        tariff_reference = instance.tariff_reference

    if tariff_reference in BiomethaneContract.TARIFF_RULE_1:
        required_fields += ["cmax", "cmax_annualized", "installation_category"]

        cmax_annualized = data.get("cmax_annualized")
        if cmax_annualized is None and instance:
            cmax_annualized = instance.cmax_annualized

        cmax_annualized_value = data.get("cmax_annualized_value")
        if cmax_annualized_value is None and instance:
            cmax_annualized_value = instance.cmax_annualized_value

        if cmax_annualized and not cmax_annualized_value:
            errors["cmax_annualized_value"] = [
                _("Le champ cmax_annualized_value est obligatoire si cmax_annualized est vrai.")
            ]

    elif tariff_reference in BiomethaneContract.TARIFF_RULE_2:
        required_fields.append("pap_contracted")

    missing_fields = []
    for field in required_fields:
        field_value = data.get(field)

        # If field is not provided in data, check the instance
        if field_value is None and instance:
            field_value = getattr(instance, field, None)

        # A field is considered missing if not in data and neither in instance
        if field_value is None:
            missing_fields.append(field)

    for field in missing_fields:
        errors[field] = [_(f"Le champ {field} est obligatoire.")]

    if errors:
        raise serializers.ValidationError(errors)

    return data


class BiomethaneContractAddSerializer(serializers.ModelSerializer):
    # Allow null to distinguish between False and not provided
    cmax_annualized = serializers.BooleanField(allow_null=True, required=False)

    class Meta:
        model = BiomethaneContract
        fields = [
            "tariff_reference",
            "buyer",
            "installation_category",
            "cmax",
            "cmax_annualized",
            "cmax_annualized_value",
            "pap_contracted",
        ]

    def validate(self, data):
        return handle_fields_requirement(data)

    def create(self, validated_data):
        entity = self.context.get("entity")

        if BiomethaneContract.objects.filter(producer=entity).exists():
            raise serializers.ValidationError({"producer": [_("Un site contract existe déjà pour cette entité.")]})
        validated_data["producer"] = entity

        if validated_data.get("cmax_annualized") is None:
            validated_data["cmax_annualized"] = False
        return super().create(validated_data)


class BiomethaneContractPatchSerializer(serializers.ModelSerializer):
    # Allow null to distinguish between False and not provided
    cmax_annualized = serializers.BooleanField(allow_null=True, required=False)

    # Allow the biomethane producer to set/unset the RED II status if the cmax or pap_contracted
    # is lower than the threshold (see biomethane contract model)
    is_red_ii = serializers.BooleanField(required=False)

    class Meta:
        model = BiomethaneContract
        fields = [
            "tariff_reference",
            "buyer",
            "installation_category",
            "cmax",
            "cmax_annualized",
            "cmax_annualized_value",
            "pap_contracted",
            "signature_date",
            "effective_date",
            "general_conditions_file",
            "specific_conditions_file",
            "is_red_ii",
        ]

    def validate(self, data):
        errors = {}
        required_fields = []

        contract_fields = [
            "signature_date",
            "effective_date",
            "general_conditions_file",
            "specific_conditions_file",
        ]

        if self.instance.does_contract_exist():
            not_updatable_fields = [field for field in contract_fields if field in data]
            for field in not_updatable_fields:
                errors[field] = [_(f"Le champ {field} ne peut pas être modifié une fois le contrat signé.")]
        else:
            # If the contract does not exist, check if any of the contract fields are provided
            for field in contract_fields:
                if field in data:
                    required_fields += contract_fields
                    continue

        return handle_fields_requirement(data, required_fields, errors, self.instance)

    def update(self, instance, validated_data):
        is_red_ii = validated_data.get("is_red_ii")
        cmax = validated_data.get("cmax")
        pap_contracted = validated_data.get("pap_contracted")

        # If cmax or pap_contracted is below the threshold and
        # the user does not want to be subject to RED II, then is_red_ii is set to False
        if is_red_ii is False and ((cmax and cmax <= 200) or (pap_contracted and pap_contracted <= 19.5)):
            instance.producer.is_red_ii = is_red_ii
            instance.producer.save()

        return super().update(instance, validated_data)
