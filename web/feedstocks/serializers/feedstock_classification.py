from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import ChoiceField

from core.models import MatierePremiere
from core.serializers import FeedStockSerializer
from feedstocks.classification_computed_attributes import CROP_TYPES_CHOICES, get_crop_type
from feedstocks.models.classification import Classification


class ClassificationSerializer(serializers.ModelSerializer):
    crop_type = serializers.SerializerMethodField()

    class Meta:
        model = Classification
        fields = ["group", "category", "subcategory", "crop_type"]

    @extend_schema_field(ChoiceField(choices=CROP_TYPES_CHOICES, allow_null=True))
    def get_crop_type(self, obj):
        return get_crop_type(obj)


class FeedStockClassificationSerializer(serializers.ModelSerializer):
    classification = ClassificationSerializer(allow_null=True)

    class Meta:
        model = MatierePremiere
        fields = FeedStockSerializer.Meta.fields + ["classification"]
