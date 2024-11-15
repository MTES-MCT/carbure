from rest_framework import serializers

from core.models import Biocarburant


class BiocarburantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biocarburant
        fields = [
            "code",
            "name",
            "description",
            "pci_kg",
            "pci_litre",
            "masse_volumique",
            "is_alcool",
            "is_graisse",
        ]
