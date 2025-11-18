from rest_framework import serializers

from core.serializers import EntityPreviewSerializer
from elec.models import ElecProvisionCertificateQualicharge


class ElecProvisionCertificateQualichargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecProvisionCertificateQualicharge
        fields = "__all__"

    cpo = EntityPreviewSerializer(read_only=True)


class StationSerializer(serializers.Serializer):
    id = serializers.RegexField(regex=r"^FR[A-Z]{3}P.*", min_length=7)
    energy = serializers.FloatField()
    is_controlled = serializers.BooleanField()


class OperationalUnitSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=5, max_length=5)
    vars()["from"] = serializers.DateField()
    to = serializers.DateField()
    stations = StationSerializer(many=True, required=False)


class ProvisionCertificateBulkSerializer(serializers.Serializer):
    entity = serializers.CharField(min_length=1)
    siren = serializers.CharField(min_length=9)
    operational_units = OperationalUnitSerializer(many=True)


class ProvisionCertificateUpdateBulkSerializer(serializers.Serializer):
    certificate_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    validated_by = serializers.ChoiceField(choices=ElecProvisionCertificateQualicharge.VALIDATION_CHOICES)
