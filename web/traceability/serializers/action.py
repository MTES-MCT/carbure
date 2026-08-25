from rest_framework import serializers

from core.serializers import EntityPreviewSerializer
from traceability.models import Action
from traceability.serializers.material import MaterialSerializer
from traceability.serializers.site import ActionSiteSerializer


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
