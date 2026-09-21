from rest_framework import serializers

from core.models import GenericCertificate


class ActionCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericCertificate
        fields = ["id", "certificate_id", "certificate_type", "certificate_holder"]
