from datetime import date

from traceability.serializers.creation import ActionCreationSerializer


class TransferSerializer(ActionCreationSerializer):
    """A quantity taken from a parent action.

    The recipient stays on the authorization fields, which the view writes as
    ``holder``. ``working_date`` is the day of the transfer. ``pos_id`` stays
    empty, because the client does not send them.
    """

    class Meta(ActionCreationSerializer.Meta):
        fields = ["quantity"]

    def create(self, validated_data):
        validated_data["working_date"] = date.today()
        return super().create(validated_data)
