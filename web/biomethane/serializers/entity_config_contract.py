from rest_framework import serializers

from biomethane.models import BiomethaneEntityConfigAmendment, BiomethaneEntityConfigContract


class BiomethaneEntityConfigAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigAmendment
        fields = [
            "id",
            "contract",
            "signature_date",
            "effective_date",
        ]


class BiomethaneEntityConfigContractSerializer(serializers.ModelSerializer):
    amendments = BiomethaneEntityConfigAmendmentSerializer(many=True, read_only=True)

    class Meta:
        model = BiomethaneEntityConfigContract
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
            "entity",
        ]


class BiomethaneEntityConfigContractAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigContract
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
        ]

    def validate(self, data):
        errors = {}
        required_fields = []

        if data.get("tariff_reference") in BiomethaneEntityConfigContract.TARIFF_RULE_1:
            required_fields.extend(["cmax", "cmax_annualized", "installation_category"])

            if data.get("cmax_annualized", False) and not data.get("cmax_annualized_value"):
                errors["cmax_annualized_value"] = [
                    "Le champ cmax_annualized_value est obligatoire si cmax_annualized est vrai."
                ]

        elif data.get("tariff_reference") in BiomethaneEntityConfigContract.TARIFF_RULE_2:
            required_fields.append("pap_contracted")

        for field in required_fields:
            if not data.get(field):
                errors[field] = [f"Le champ {field} est obligatoire pour l'arrêté tarifaire {data.get('tariff_reference')}."]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class BiomethaneEntityConfigContractPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigContract
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
        ]

    def validate(self, data):
        # errors = {}
        # required_fields = []

        print("Validating data:", data)
        print("instance : ", self.instance)

        # Rules : si
        #    "signature_date",
        #    "effective_date",
        #    "general_conditions_file",
        #    "specific_conditions_file",
        # existent déjà, on ne peut pas les modifier
        #
        # dans le cas contraire, on peut les insérer mais ils sont tous obligatoires

        return data
