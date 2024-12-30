from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, required=True)
