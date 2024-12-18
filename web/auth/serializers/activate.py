from rest_framework import serializers


class ActivateAccountSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    invite = serializers.IntegerField(required=False)
