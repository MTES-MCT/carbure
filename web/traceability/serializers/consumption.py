from rest_framework import serializers

from traceability.models import Action
from traceability.serializers.action_create import ActionCreateSerializer
from traceability.serializers.lookups import CertificateLookupField, MaterialLookupField, SiteLookupField


class ConsumptionSerializer(ActionCreateSerializer):
    type = serializers.ChoiceField(choices=[Action.INIT])
    material = MaterialLookupField(required=False, allow_null=True)
    certificate = CertificateLookupField(required=False, allow_null=True)
    site = SiteLookupField(required=False, allow_null=True)

    class Meta(ActionCreateSerializer.Meta):
        fields = [
            *ActionCreateSerializer.Meta.fields,
            "pos_id",
            "material",
            "certificate",
            "quantity",
            "site",
            "shipping_date",
            "shipping_distance",
            "shipping_method",
            "working_date",
            "eec",
            "el",
            "ei",
            "ep",
            "etd",
            "eu",
            "eccs",
            "esca",
            "eccr",
        ]
