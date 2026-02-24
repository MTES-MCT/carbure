from rest_framework import serializers

from core.models import MatierePremiere
from core.serializers import FeedStockSerializer
from feedstocks.models.classification import Classification


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ["group", "category", "subcategory"]


class FeedStockClassificationSerializer(serializers.ModelSerializer):
    classification = ClassificationSerializer(allow_null=True)

    class Meta:
        model = MatierePremiere
        fields = FeedStockSerializer.Meta.fields + ["classification"]
