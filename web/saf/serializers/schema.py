from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class YearSerializer(serializers.Serializer):
    year = serializers.IntegerField()


class CommentSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False)
