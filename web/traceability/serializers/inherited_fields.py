from rest_framework import serializers

from traceability.serializers.material import MaterialSerializer


class ActionInheritedFieldsSerializer(serializers.Serializer):
    """Nearest declared values along the parent chain, including the action itself."""

    material = MaterialSerializer(allow_null=True)
