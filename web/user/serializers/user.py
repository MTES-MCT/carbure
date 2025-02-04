from rest_framework import serializers

from core.serializers import UserRightsRequestsSerializer, UserRightsSerializer


class UserSettingsResponseSeriaizer(serializers.Serializer):
    email = serializers.EmailField()
    rights = UserRightsSerializer(many=True)
    requests = UserRightsRequestsSerializer(many=True)


class ResponseSuccessSerializer(serializers.Serializer):
    status = serializers.CharField()
