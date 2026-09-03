from decimal import Decimal

from rest_framework import serializers

from traceability.serializers.action import ActionExcelImportSerializer


class H2ActionExcelImportSerializer(ActionExcelImportSerializer):
    """H2 Excel extras: validated then discarded, not stored on Action."""

    lot_id = serializers.CharField(write_only=True)
    lot_quantity = serializers.DecimalField(max_digits=13, decimal_places=3, min_value=Decimal("0"), write_only=True)
    producer = serializers.CharField(write_only=True)

    class Meta(ActionExcelImportSerializer.Meta):
        fields = [*ActionExcelImportSerializer.Meta.fields, "lot_id", "lot_quantity", "producer"]
