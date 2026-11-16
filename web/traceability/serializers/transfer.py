import uuid

from traceability.serializers.creation import ActionCreationSerializer


class TransferSerializer(ActionCreationSerializer):
    """A quantity taken from a parent action.

    The recipient stays on the authorization fields, which the view writes as
    ``holder``. ``pos_id`` is generated and ``working_date`` is copied from the
    parent, because the client does not send them.
    """

    class Meta(ActionCreationSerializer.Meta):
        fields = ["quantity"]

    def create(self, validated_data):
        parent = validated_data["parent"]
        validated_data["pos_id"] = str(uuid.uuid4())
        validated_data["working_date"] = parent.working_date
        return super().create(validated_data)
