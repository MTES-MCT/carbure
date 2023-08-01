from rest_framework import serializers
from elec.models import ElecProvisionCertificate


class ElecProvisionCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecProvisionCertificate
        fields = [
            "cpo",
            "quarter",
            "year",
            "operating_unit",
            "energy_amount",
            "remaining_energy_amount",
        ]
