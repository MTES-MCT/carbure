from rest_framework import serializers

from biomethane.models import BiomethaneDigestateStorage


class BiomethaneDigestateStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneDigestateStorage
        fields = [
            "id",
            "producer",
            "type",
            "capacity",
            "has_cover",
            "has_biogas_recovery",
        ]


class BiomethaneDigestateStorageAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneDigestateStorage
        fields = [
            "type",
            "capacity",
            "has_cover",
            "has_biogas_recovery",
        ]

    def create(self, validated_data):
        entity = self.context.get("entity")
        validated_data["producer"] = entity

        return super().create(validated_data)


class BiomethaneDigestateStoragePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneDigestateStorage
        fields = [
            "type",
            "capacity",
            "has_cover",
            "has_biogas_recovery",
        ]
