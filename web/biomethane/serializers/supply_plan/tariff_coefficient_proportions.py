from rest_framework import serializers


class TariffCoefficientProportionsSerializer(serializers.Serializer):
    p1 = serializers.FloatField()
    p2 = serializers.FloatField()
    p3 = serializers.FloatField()
    p = serializers.FloatField()
    peff = serializers.FloatField()
