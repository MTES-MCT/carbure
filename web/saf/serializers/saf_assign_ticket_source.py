from rest_framework import serializers

from transactions.models.site import Site


class SafTicketSourceAssignmentSerializer(serializers.Serializer):
    client_id = serializers.IntegerField(required=True)
    volume = serializers.FloatField(required=True)
    agreement_reference = serializers.CharField(required=False)
    agreement_date = serializers.CharField(required=False)
    free_field = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    assignment_period = serializers.IntegerField(required=True)
    reception_airport = serializers.PrimaryKeyRelatedField(
        queryset=Site.objects.filter(site_type=Site.AIRPORT), required=False, allow_null=True
    )
    consumption_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    shipping_method = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SafTicketSourceGroupAssignmentSerializer(SafTicketSourceAssignmentSerializer):
    ticket_sources_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

    def validate_ticket_sources_ids(self, value):
        if not value:
            raise serializers.ValidationError("Ticket sources ids cannot be empty.")
        return value
