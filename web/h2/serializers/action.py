from rest_framework import serializers

from traceability.serializers.action import ActionExcelImportSerializer


class H2ActionExcelImportSerializer(ActionExcelImportSerializer):
    """H2 Excel extras: validated then discarded, not stored on Action."""

    lot_id = serializers.CharField(write_only=True)

    class Meta(ActionExcelImportSerializer.Meta):
        fields = [*ActionExcelImportSerializer.Meta.fields, "lot_id"]
