from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecProvisionCertificate


class ElecProvisionCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecProvisionCertificate
        fields = [
            "id",
            "cpo",
            "quarter",
            "year",
            "operating_unit",
            "energy_amount",
            "remaining_energy_amount",
        ]

    cpo = EntityPreviewSerializer(read_only=True)
