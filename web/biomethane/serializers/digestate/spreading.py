from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading


class BaseBiomethaneDigestateSpreadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneDigestateSpreading
        exclude = ["digestate"]


class BiomethaneDigestateSpreadingSerializer(BaseBiomethaneDigestateSpreadingSerializer):
    class Meta(BaseBiomethaneDigestateSpreadingSerializer.Meta):
        exclude = []


class BiomethaneDigestateSpreadingAddSerializer(BaseBiomethaneDigestateSpreadingSerializer):
    def create(self, validated_data):
        entity = self.context.get("entity")
        year = self.context.get("year")

        digestate = BiomethaneDigestate.objects.filter(producer=entity, year=year).first()

        if not digestate:
            raise serializers.ValidationError({"year": [_("Digestat manquant.")]})

        validated_data["digestate"] = digestate

        return super().create(validated_data)
