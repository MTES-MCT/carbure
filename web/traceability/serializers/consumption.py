from rest_framework import serializers

from traceability.models import Action
from traceability.serializers.lookups import CertificateLookupField, MaterialLookupField, SiteLookupField


class ConsumptionSerializer(serializers.ModelSerializer):
    type = serializers.HiddenField(default=Action.INIT)
    material = MaterialLookupField(required=False, allow_null=True)
    certificate = CertificateLookupField(required=False, allow_null=True)
    site = SiteLookupField(required=False, allow_null=True)

    class Meta:
        model = Action
        fields = [
            "type",
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
