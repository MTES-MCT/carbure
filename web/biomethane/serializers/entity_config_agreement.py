from rest_framework import serializers

from biomethane.models import BiomethaneEntityConfigAgreement, BiomethaneEntityConfigAmendment


class BiomethaneEntityConfigAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigAgreement
        fields = [
            "entity",
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


class BiomethaneEntityConfigAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigAmendment
        fields = [
            "id",
            "contract",
            "signature_date",
            "effective_date",
            "amendment_object",
        ]
