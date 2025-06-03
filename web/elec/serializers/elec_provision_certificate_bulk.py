from rest_framework import serializers


class StationSerializer(serializers.Serializer):
    id = serializers.RegexField(regex=r"^FR[A-Z]{3}P.*", min_length=7)
    energy = serializers.FloatField(min_value=1)
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
