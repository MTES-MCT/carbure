from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from doublecount.serializers import DoubleCountingProductionSerializer, DoubleCountingSourcingSerializer


class FileErrorSerializer(serializers.Serializer):
    error = serializers.CharField()
    is_blocking = serializers.BooleanField()
    line_number = serializers.IntegerField()
    line_merged = serializers.CharField()
    meta = serializers.DictField()


class FileErrorsSerializer(serializers.Serializer):
    sourcing_forecast = serializers.ListField(child=FileErrorSerializer())
    sourcing_history = serializers.ListField(child=FileErrorSerializer())
    production = serializers.ListField(child=FileErrorSerializer())
    global_errors = serializers.ListField(child=FileErrorSerializer())


class FileSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    errors = FileErrorsSerializer()
    error_count = serializers.IntegerField()
    start_year = serializers.IntegerField()
    production_site = serializers.CharField()
    producer_email = serializers.EmailField()
    production = serializers.ListField(child=DoubleCountingProductionSerializer())
    sourcing = serializers.ListField(child=DoubleCountingSourcingSerializer())
    # sourcing_history = serializers.ListField(child=DoubleCountingSourcingHistorySerializer())
    has_dechets_industriels = serializers.SerializerMethodField()

    @extend_schema_field(bool)
    def get_has_dechets_industriels(self, obj):
        return False


class CheckFileResponseSerializer(serializers.Serializer):
    file = FileSerializer()
    checked_at = serializers.DateTimeField()


class ResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
