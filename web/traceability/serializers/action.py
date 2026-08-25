from rest_framework import serializers

from core.serializer_fields import CachedSlugRelatedField
from core.serializers import EntityPreviewSerializer
from traceability.models import Action, Material
from traceability.models.action_status import ActionStatus
from traceability.serializers.material import MaterialSerializer
from traceability.serializers.site import ActionSiteSerializer
from transactions.models import Site


class ActionParentSerializer(serializers.ModelSerializer):
    """Small representation used for the parent action relation."""

    class Meta:
        model = Action
        fields = ["id", "pos_id"]


class ActionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    holder = EntityPreviewSerializer(read_only=True)
    parent = ActionParentSerializer(read_only=True, required=False, allow_null=True)
    material = MaterialSerializer(read_only=True)
    site = ActionSiteSerializer(read_only=True)

    class Meta:
        model = Action
        fields = "__all__"


class ActionInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        exclude = ["id"]


class ActionQuerySerializer(serializers.Serializer):
    industry = serializers.ChoiceField(choices=Action.INDUSTRIES)


class ActionExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class ActionExcelImportSerializer(serializers.ModelSerializer):
    material = CachedSlugRelatedField(slug_field="name", queryset=Material.objects.all(), cache_key="material_cache")
    site = CachedSlugRelatedField(slug_field="name", queryset=Site.objects.all(), cache_key="site_cache")

    class Meta:
        model = Action
        fields = [
            "pos_id",
            "material",
            "quantity",
            "site",
            "shipping_date",
            "shipping_distance",
            "shipping_method",
            "ei",
            "ep",
            "etd",
            "eu",
            "eccs",
        ]

    def create(self, validated_data):
        action = Action.objects.create(
            **validated_data,
            holder=self.context["entity"],
            industry=self.context["handler"].industry,
            type=Action.INIT,
            working_date=validated_data["shipping_date"],
        )
        ActionStatus.objects.create(action=action, status=ActionStatus.CREATED)
        return action
