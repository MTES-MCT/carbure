from rest_framework import serializers

from core.models import Entity
from saf.models.saf_logistics import SafLogistics
from saf.models.saf_ticket import SafTicket
from transactions.models.airport import Airport

SAF_TYPES = [Entity.OPERATOR, Entity.AIRLINE, Entity.SAF_TRADER]
CONSUMPTION_TYPES = [choice[0] for choice in SafTicket.CONSUMPTION_TYPES]
SHIPPING_METHODS = [choice[0] for choice in SafLogistics.SHIPPING_METHODS]


class SafTicketSourceAssignmentSerializer(serializers.Serializer):
    client_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.filter(entity_type__in=SAF_TYPES), required=True)
    volume = serializers.FloatField(required=True, min_value=1)
    agreement_reference = serializers.CharField(required=False, allow_blank=True)
    agreement_date = serializers.CharField(required=False)
    free_field = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    assignment_period = serializers.IntegerField(required=True)
    reception_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all(), required=False, allow_null=True)
    consumption_type = serializers.ChoiceField(required=False, allow_null=True, allow_blank=True, choices=CONSUMPTION_TYPES)
    shipping_method = serializers.ChoiceField(required=False, allow_null=True, allow_blank=True, choices=SHIPPING_METHODS)
    has_intermediary_depot = serializers.BooleanField(required=False, default=False)
    pos_number = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        client = attrs["client_id"]
        errors = {}

        if client.entity_type in [Entity.AIRLINE, Entity.SAF_TRADER] and not attrs.get("reception_airport"):
            errors["reception_airport"] = "This field is required for airline and SAF trader clients."

        if client.entity_type == Entity.OPERATOR and not attrs.get("agreement_reference"):
            errors["agreement_reference"] = "This field is required for operator clients."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class SafTicketSourceGroupAssignmentSerializer(SafTicketSourceAssignmentSerializer):
    ticket_sources_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

    def validate_ticket_sources_ids(self, value):
        if not value:
            raise serializers.ValidationError("Ticket sources ids cannot be empty.")
        return value
