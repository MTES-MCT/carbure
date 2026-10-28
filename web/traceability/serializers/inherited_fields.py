from rest_framework import serializers

from core.serializers import EntityPreviewSerializer
from traceability.serializers.material import MaterialSerializer
from traceability.serializers.site import ActionSiteSerializer


class ActionInheritedFieldsSerializer(serializers.Serializer):
    """Every value the front receives from the parent-chain walk.

    previous_material is the nearest declared material above the action.
    origin_material is the first declared material from the root. It is the action's
    own material when nothing above declares one.
    nearest_site is the first site above the action. The action's own site is ignored.
    producer and root_pos are the holder and the pos_id of the root.
    """

    previous_material = MaterialSerializer(allow_null=True)
    origin_material = MaterialSerializer(allow_null=True)
    nearest_site = ActionSiteSerializer(allow_null=True)
    producer = EntityPreviewSerializer()
    root_pos = serializers.CharField()
