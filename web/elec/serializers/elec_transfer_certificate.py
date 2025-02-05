from rest_framework import serializers

from core.serializers import EntityPreviewSerializer
from elec.models import ElecTransferCertificate


class ElecTransferCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecTransferCertificate
        fields = [
            "id",
            "supplier",
            "client",
            "transfer_date",
            "energy_amount",
            "status",
            "certificate_id",
        ]

    supplier = EntityPreviewSerializer(read_only=True)
    client = EntityPreviewSerializer(read_only=True)


class ElecTransferCertificateDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecTransferCertificate
        fields = [
            "id",
            "supplier",
            "client",
            "transfer_date",
            "energy_amount",
            "status",
            "certificate_id",
            "comment",
            "used_in_tiruert",
            "consumption_date",
        ]

    supplier = EntityPreviewSerializer(read_only=True)
    client = EntityPreviewSerializer(read_only=True)
