from rest_framework import serializers

from traceability.models import Material


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "code", "name", "lhv", "density"]
