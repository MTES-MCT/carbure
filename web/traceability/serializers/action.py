from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.serializer_fields import LabelChoiceField
from core.serializer_validators import UniqueInListSerializer
from core.serializers import EntityPreviewSerializer
from traceability.models import Action, Industry
from traceability.models.action_status import ActionStatus
from traceability.serializers.certificate import ActionCertificateSerializer
from traceability.serializers.fields import (
    EMISSION_DECIMAL,
    ExcelDateField,
    ExcelMonthYearField,
    TruncatingDecimalField,
)
from traceability.serializers.inherited_fields import ActionInheritedFieldsSerializer
from traceability.serializers.lookups import CertificateLookupField, MaterialLookupField, SiteLookupField
from traceability.serializers.material import MaterialSerializer
from traceability.serializers.site import ActionSiteSerializer
from traceability.serializers.total_emissions import ActionTotalEmissionsSerializer
from traceability.services.action_import_file import store_action_import_file


class ActionParentSerializer(serializers.ModelSerializer):
    """Small representation used for the parent action relation."""

    holder = EntityPreviewSerializer(read_only=True)

    class Meta:
        model = Action
        fields = ["id", "pos_id", "working_date", "holder"]


class ActionSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=ActionStatus.STATUSES, read_only=True, allow_null=True)
    holder = EntityPreviewSerializer(read_only=True)
    parent = ActionParentSerializer(read_only=True, required=False, allow_null=True)
    material = MaterialSerializer(read_only=True, allow_null=True)
    site = ActionSiteSerializer(read_only=True)
    certificate = ActionCertificateSerializer(read_only=True, allow_null=True)

    total_emissions = ActionTotalEmissionsSerializer(read_only=True, allow_null=True)
    inherited_fields = ActionInheritedFieldsSerializer(read_only=True)
    quantity_available = serializers.DecimalField(max_digits=13, decimal_places=3, read_only=True, default=0)
    carbure_id = serializers.CharField(read_only=True, label="Identifiant Carbure")

    class Meta:
        model = Action
        exclude = ["file"]


class ActionQuerySerializer(serializers.Serializer):
    industry = serializers.ChoiceField(choices=Industry.choices)


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
            actions = []
            for attrs in validated_data:
                actions.append(
                    Action(
                        **{key: value for key, value in attrs.items() if key in _ACTION_MODEL_FIELDS},
                        holder=holder,
                        industry=industry,
                        type=Action.CONSUME,
                    )
                )

            return Action.bulk_create(actions, default_status=ActionStatus.PENDING)
        except Exception:
            stored_file.url.delete(save=False)
            raise


class ActionExcelImportSerializer(serializers.ModelSerializer):
    material = MaterialLookupField()
    certificate = CertificateLookupField(required=True, allow_null=False)
    site = SiteLookupField()
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
    quantity = TruncatingDecimalField(
        max_digits=13,
        decimal_places=3,
        min_value=Decimal("0.001"),
        error_messages={"min_value": _("La quantité doit être strictement positive.")},
    )
    eec = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    el = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    ei = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    ep = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    etd = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    eu = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    eccs = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    esca = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)
    eccr = TruncatingDecimalField(**EMISSION_DECIMAL, required=False)

    class Meta:
        model = Action
        list_serializer_class = ActionExcelImportListSerializer
        extra_kwargs = {"pos_id": {"required": True, "allow_null": False, "allow_blank": False}}
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
