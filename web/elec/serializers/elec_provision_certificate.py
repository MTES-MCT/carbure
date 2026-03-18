from rest_framework import serializers

from core.serializers import EntityPreviewSerializer
from elec.models import ElecProvisionCertificate


class ElecProvisionCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecProvisionCertificate
        fields = [
            "id",
            "cpo",
            "source",
            "quarter",
            "year",
            "date_from",
            "date_to",
            "month",
            "operating_unit",
            "energy_amount",
            "created_at",
        ]

    cpo = EntityPreviewSerializer(read_only=True)
    month = serializers.SerializerMethodField()

    def get_month(self, obj):
        if obj.date_from:
            return f"{obj.date_from.strftime('%m/%Y')}"
        return None
