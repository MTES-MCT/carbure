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
from traceability.serializers.total_emissions import ActionTotalEmissionsSerializer
from traceability.services.action_import_file import store_action_import_file


class ActionParentSerializer(serializers.ModelSerializer):
    """Small representation used for the parent action relation."""

    class Meta:
        model = Action
        fields = ["id", "pos_id"]


class ActionSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES, read_only=True, allow_null=True)
    holder = EntityPreviewSerializer(read_only=True)
    parent = ActionParentSerializer(read_only=True, required=False, allow_null=True)
    material = MaterialSerializer(read_only=True)
    site = ActionSiteSerializer(read_only=True)
    certificate = ActionCertificateSerializer(read_only=True, allow_null=True)

    total_emissions = ActionTotalEmissionsSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Action
        exclude = ["file"]


class ActionInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        exclude = ["file"]
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
        stored_file = store_action_import_file(
            self.context["import_file"],
            entity=holder,
            user=self.context["request"].user,
        )
        for action_data in validated_data:
            action_data["file"] = stored_file

        try:
            actions = [
                Action(
                    **{key: value for key, value in action_data.items() if key in _ACTION_MODEL_FIELDS},
                    holder=holder,
                    industry=industry,
                    type=Action.INIT,
                )
                for action_data in validated_data
            ]

            return Action.bulk_create(actions, default_status=ActionStatus.PENDING)
        except Exception:
            stored_file.url.delete(save=False)
            raise


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
            "eec",
            "el",
            "ei",
            "ep",
            "etd",
            "eu",
            "eccs",
            "esca",
            "eccr",
            "working_date",
        ]
