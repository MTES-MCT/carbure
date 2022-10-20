from rest_framework import serializers

from saf.models import SafTicket


class SafTicketPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
            "client",
            "agreement_date",
            "volume",
            "status",
        ]

    client = serializers.SlugRelatedField(read_only=True, slug_field="name")
