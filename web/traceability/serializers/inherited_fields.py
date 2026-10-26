from rest_framework import serializers

from traceability.serializers.material import MaterialSerializer


class ActionInheritedFieldsSerializer(serializers.Serializer):
    """Materials resolved along the parent chain.

    previous_material is the nearest declared material above the action.
    origin_material is the first declared material from the root. It is the action's
    own material when nothing above declares one.
    """

    previous_material = MaterialSerializer(allow_null=True)
    origin_material = MaterialSerializer(allow_null=True)
