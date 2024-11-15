from rest_framework import serializers

from core.models import MatierePremiere


class MatierePremiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatierePremiere
        fields = [
            "code",
            "name",
            "description",
            "compatible_alcool",
            "compatible_graisse",
            "is_double_compte",
            "category",
        ]
