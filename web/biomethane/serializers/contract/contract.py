from datetime import date

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

        if not contract and "tariff_reference" not in validated_data:
            errors["tariff_reference"] = [_("Ce champ est obligatoire pour la création d'un contrat.")]

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
            required_fields += ["cmax", "cmax_annualized", "installation_category", "buyer"]

            cmax_annualized = validated_data.get("cmax_annualized")
            cmax_annualized_value = validated_data.get("cmax_annualized_value")

            if cmax_annualized and not cmax_annualized_value:
                errors["cmax_annualized_value"] = [
                    _("Le champ cmax_annualized_value est obligatoire si cmax_annualized est vrai.")
                ]

        # Tariff rule 2
        elif tariff_reference in BiomethaneContract.TARIFF_RULE_2:
            required_fields += ["pap_contracted", "installation_category", "buyer"]

        # Rules regarding contract dates
        signature_date = validated_data.get("signature_date")
        effective_date = validated_data.get("effective_date")

        if signature_date and effective_date:
            if effective_date <= signature_date:
                errors["effective_date"] = [_("La date d'effet doit être postérieure à la date de signature.")]

            # 2011 : 23/11/2011 et 23/11/2020
            if tariff_reference == "2011" and not (
                signature_date >= date(2011, 11, 23) and signature_date <= date(2020, 11, 23)
            ):
                errors["signature_date"] = [
                    _(
                        (
                            "Pour la référence tarifaire 2011, la date de signature doit être entre "
                            "le 23/11/2011 et le 23/11/2020."
                        )
                    )
                ]
            # 2020 : 23/11/2020 et 13/12/2021
            if tariff_reference == "2020" and not (
                signature_date >= date(2020, 11, 23) and signature_date <= date(2021, 12, 13)
            ):
                errors["signature_date"] = [
                    _(
                        (
                            "Pour la référence tarifaire 2020, la date de signature doit être entre "
                            "le 23/11/2020 et le 13/12/2021."
                        )
                    )
                ]
            # 2021, 13/12/2021 et 10/06/2023
            if tariff_reference == "2021" and not (
                signature_date >= date(2021, 12, 13) and signature_date <= date(2023, 6, 10)
            ):
                errors["signature_date"] = [
                    _(
                        (
                            "Pour la référence tarifaire 2021, la date de signature doit être entre "
                            "le 13/12/2021 et le 10/06/2023."
                        )
                    )
                ]
            # 2023, date de signature > 10/06/2023
            if tariff_reference == "2023" and not (signature_date and signature_date > date(2023, 6, 10)):
                errors["signature_date"] = [
                    _("Pour la référence tarifaire 2023, la date de signature doit être postérieure au 10/06/2023.")
                ]

        for field in required_fields:
            if validated_data.get(field) in [None, ""]:
                errors[field] = [_("Ce champ est obligatoire.")]

        if errors:
            raise serializers.ValidationError(errors)

        return validated_data

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["producer"] = entity
        self.handle_is_red_ii(validated_data, entity)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.handle_is_red_ii(validated_data, instance.producer)
        return super().update(instance, validated_data)

    def handle_is_red_ii(self, validated_data, producer):
        is_red_ii = validated_data.pop("is_red_ii", None)
        cmax = validated_data.get("cmax", None)
        pap_contracted = validated_data.get("pap_contracted", None)

        # If cmax or pap_contracted is below the threshold and
        # the user does not want to be subject to RED II, then is_red_ii is set to False
        if is_red_ii is False and ((cmax and cmax <= 200) or (pap_contracted and pap_contracted <= 19.5)):
            producer.is_red_ii = is_red_ii
            producer.save(update_fields=["is_red_ii"])
