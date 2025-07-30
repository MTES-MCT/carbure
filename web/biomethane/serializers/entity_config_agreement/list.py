from rest_framework import serializers

from biomethane.models import BiomethaneEntityConfigAgreement, BiomethaneEntityConfigAmendment


class BiomethaneEntityConfigAmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEntityConfigAmendment
        fields = [
            "id",
            "contract",
            "signature_date",
            "effective_date",
        ]


class BiomethaneEntityConfigAgreementSerializer(serializers.ModelSerializer):
    amendments = BiomethaneEntityConfigAmendmentSerializer(many=True, read_only=True)

    class Meta:
        model = BiomethaneEntityConfigAgreement
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
        ]
