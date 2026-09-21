from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from traceability.serializers.action import ActionExcelImportSerializer


class H2ActionExcelImportSerializer(ActionExcelImportSerializer):
    """H2 Excel extras: validated then discarded, not stored on Action."""

    lot_id = serializers.CharField(write_only=True)
    lot_quantity = serializers.DecimalField(max_digits=13, decimal_places=3, min_value=Decimal("0"), write_only=True)
    producer = serializers.CharField(write_only=True)
    consumed_on_production_site = serializers.ChoiceField(
        choices=["Oui", "Non"],
        write_only=True,
        error_messages={"invalid_choice": _("La valeur doit être Oui ou Non.")},
    )
    etd1 = serializers.DecimalField(max_digits=7, decimal_places=3, min_value=Decimal("0"), write_only=True)
    etd2 = serializers.DecimalField(max_digits=7, decimal_places=3, min_value=Decimal("0"), write_only=True)

    class Meta(ActionExcelImportSerializer.Meta):
        fields = [
            *ActionExcelImportSerializer.Meta.fields,
            "lot_id",
            "lot_quantity",
            "producer",
            "consumed_on_production_site",
            "etd1",
            "etd2",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["etd"] = attrs.pop("etd1") + attrs.pop("etd2")
        return attrs
