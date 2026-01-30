from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Entity
from core.serializers import EntityPreviewSerializer
from elec.models import ElecProvisionCertificateQualicharge


class ElecProvisionCertificateQualichargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecProvisionCertificateQualicharge
        fields = "__all__"

    cpo = EntityPreviewSerializer(read_only=True)
    renewable_energy = serializers.FloatField()


class ElecProvisionCertificateQualichargeGroupedSerializer(serializers.Serializer):
    """Serializer for grouped provision certificate data by operating unit."""

    cpo = serializers.SerializerMethodField()
    operating_unit = serializers.CharField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    year = serializers.IntegerField()
    energy_amount = serializers.FloatField()
    renewable_energy = serializers.FloatField()

    @extend_schema_field(EntityPreviewSerializer())
    def get_cpo(self, obj):
        return {
            "id": obj.get("cpo__id"),
            "name": obj.get("cpo__name"),
            "entity_type": obj.get("cpo__entity_type"),
            "registration_id": obj.get("cpo__registration_id"),
        }


class StationSerializer(serializers.Serializer):
    id = serializers.RegexField(regex=r"^FR[A-Z0-9]{3}P.*", min_length=7)
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
    certificate_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    validated_by = serializers.ChoiceField(choices=ElecProvisionCertificateQualicharge.VALIDATION_CHOICES)
    cpo = serializers.ListField(
        child=serializers.SlugRelatedField(slug_field="name", queryset=Entity.objects.all()), required=False
    )
    status = serializers.ListField(
        child=serializers.ChoiceField(choices=ElecProvisionCertificateQualicharge.VALIDATION_CHOICES),
        required=False,
    )
    operating_unit = serializers.ListField(child=serializers.CharField(), required=False)
    station_id = serializers.ListField(child=serializers.CharField(), required=False)
    date_from = serializers.ListField(child=serializers.DateField(), required=False)


class TransferCertificateSerializer(serializers.Serializer):
    certificate_id = serializers.IntegerField(required=True)
    target_entity_id = serializers.IntegerField(required=True)

    def validate(self, validated_data):
        certificate_id = validated_data["certificate_id"]
        target_entity_id = validated_data["target_entity_id"]

        try:
            certificate = ElecProvisionCertificateQualicharge.objects.get(id=certificate_id)
        except ElecProvisionCertificateQualicharge.DoesNotExist:
            raise serializers.ValidationError({"certificate_id": "Certificate not found"})

        if not certificate.cpo:
            raise serializers.ValidationError({"certificate_id": "Certificate has no CPO assigned"})

        request = self.context.get("request")
        if request and hasattr(request, "entity") and certificate.cpo != request.entity:
            raise serializers.ValidationError({"certificate_id": "Certificate does not belong to the caller entity"})

        if certificate.validated_by == ElecProvisionCertificateQualicharge.BOTH:
            raise serializers.ValidationError({"certificate_id": "Cannot transfer a double-validated certificate"})

        try:
            target_entity = Entity.objects.get(id=target_entity_id)
        except Entity.DoesNotExist:
            raise serializers.ValidationError({"target_entity_id": "Target entity not found"})

        if certificate.cpo.registration_id != target_entity.registration_id:
            raise serializers.ValidationError(
                {
                    "target_entity_id": "Target entity must have the same registration ID as the current CPO",
                }
            )

        validated_data["certificate"] = certificate
        validated_data["target_entity"] = target_entity
        return validated_data
