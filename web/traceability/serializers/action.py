from django.utils import timezone
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
        fields = "__all__"
        read_only_fields = ["id", "industry", "holder", "parent"]

    def create(self, validated_data):
        validated_data["industry"] = self.context["handler"].industry
        validated_data["holder"] = self.context["entity"]
        return super().create(validated_data)


class ActionQuerySerializer(serializers.Serializer):
    industry = serializers.ChoiceField(choices=Action.INDUSTRIES)


class ActionExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class HandlerLookupSlugRelatedField(CachedSlugRelatedField):
    def __init__(self, *args, lookup, **kwargs):
        self.lookup = lookup
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return getattr(self.context["handler"].lookups, self.lookup)(self.context.get("entity"))


class ActionExcelImportListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        holder = self.context["entity"]
        industry = self.context["handler"].industry
        actions = [
            Action(
                **attrs,
                holder=holder,
                industry=industry,
                type=Action.INIT,
                working_date=attrs["shipping_date"],
            )
            for attrs in validated_data
        ]
        Action.objects.bulk_create(actions)

        created_actions = list(Action.objects.filter(pos_id__in=[action.pos_id for action in actions]))
        created_at = timezone.now()
        ActionStatus.objects.bulk_create(
            ActionStatus(action=action, status=ActionStatus.CREATED, created_at=created_at) for action in created_actions
        )

        return created_actions


class ActionExcelImportSerializer(serializers.ModelSerializer):
    material = HandlerLookupSlugRelatedField(
        slug_field="name",
        queryset=Material.objects.all(),
        cache_key="material_cache",
        lookup="material",
    )
    site = HandlerLookupSlugRelatedField(
        slug_field="name",
        queryset=Site.objects.all(),
        cache_key="site_cache",
        lookup="site",
    )

    class Meta:
        model = Action
        list_serializer_class = ActionExcelImportListSerializer
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
