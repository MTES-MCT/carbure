from rest_framework import serializers


class ProductionSerializer(serializers.Serializer):
    volume = serializers.FloatField()
    unit = serializers.CharField()


class SourcingSerializer(serializers.Serializer):
    country = serializers.CharField()
    method = serializers.CharField()


class SourcingHistorySerializer(serializers.Serializer):
    changes = serializers.IntegerField()
    last_update = serializers.DateField()


class FileErrorsSerializer(serializers.Serializer):
    sourcing_forecast = serializers.ListField(child=serializers.CharField())
    sourcing_history = serializers.ListField(child=serializers.CharField())
    production = serializers.ListField(child=serializers.CharField())
    global_errors = serializers.ListField(child=serializers.CharField())


class FileSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    errors = FileErrorsSerializer()
    error_count = serializers.IntegerField()
    start_year = serializers.IntegerField()
    production_site = serializers.CharField()
    producer_email = serializers.EmailField()
    production = serializers.ListField(child=ProductionSerializer())
    sourcing = serializers.ListField(child=SourcingSerializer())
    sourcing_history = serializers.ListField(child=SourcingHistorySerializer())


class CheckFileResponseSerializer(serializers.Serializer):
    file = FileSerializer()
    checked_at = serializers.DateTimeField()


class ResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
