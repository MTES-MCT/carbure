from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.serializer_fields import LabelChoiceField
from core.serializer_validators import UniqueInListSerializer
from core.serializers import EntityPreviewSerializer
from traceability.models import Action
from traceability.models.action_status import ActionStatus
from traceability.serializers.certificate import ActionCertificateSerializer
from traceability.serializers.fields import ExcelDateField, ExcelMonthYearField, LookupSlugRelatedField
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
    certificate = ActionCertificateSerializer(read_only=True, allow_null=True)

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


_ACTION_MODEL_FIELDS = {field.name for field in Action._meta.fields}


class ActionExcelImportListSerializer(UniqueInListSerializer):
    unique_fields = ["pos_id"]

    def create(self, validated_data):
        holder = self.context["entity"]
        industry = self.context["handler"].industry
        actions = [
            Action(
                **{key: value for key, value in attrs.items() if key in _ACTION_MODEL_FIELDS},
                holder=holder,
                industry=industry,
                type=Action.INIT,
            )
            for attrs in validated_data
        ]
        Action.objects.bulk_create(actions)

        created_actions = list(Action.objects.filter(pos_id__in=[action.pos_id for action in actions]))
        created_at = timezone.now()
        ActionStatus.objects.bulk_create(
            ActionStatus(action=action, status=ActionStatus.PENDING, created_at=created_at) for action in created_actions
        )

        return created_actions


class ActionExcelImportSerializer(serializers.ModelSerializer):
    material = LookupSlugRelatedField(
        slug_field="name",
        lookup="material",
        error_messages={"does_not_exist": _("Matière inconnue")},
    )
    certificate = LookupSlugRelatedField(
        slug_field="certificate_id",
        lookup="certificate",
        required=True,
        allow_null=False,
        error_messages={"does_not_exist": _("Certificat inconnu")},
    )
    site = LookupSlugRelatedField(
        slug_field="name",
        lookup="site",
        error_messages={"does_not_exist": _("Site inconnu")},
    )
    shipping_date = ExcelDateField(
        input_formats=["%d/%m/%Y"],
        error_messages={"invalid": _("La date doit être au format jour/mois/année.")},
        allow_null=True,
    )
    working_date = ExcelMonthYearField(
        input_formats=["%m/%Y"],
        error_messages={"invalid": _("La période doit être au format mois/année.")},
    )
    shipping_method = LabelChoiceField(choices=Action.SHIPPING_METHODS, required=False, allow_blank=True)

    class Meta:
        model = Action
        list_serializer_class = ActionExcelImportListSerializer
        fields = [
            "pos_id",
            "material",
            "certificate",
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
            "working_date",
        ]
