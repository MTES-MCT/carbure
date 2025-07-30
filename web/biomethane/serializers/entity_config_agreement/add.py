from rest_framework import serializers

from biomethane.models import BiomethaneEntityConfigAgreement


class BiomethaneEntityConfigAgreementAddSerializer(serializers.ModelSerializer):
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
        ]
