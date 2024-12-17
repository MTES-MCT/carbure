from rest_framework import serializers

from core.models import Entity


class RequestAccessSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False)
    role = serializers.CharField()
    entity_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())


class RevokeAccessSerializer(serializers.Serializer):
    entity_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all())
