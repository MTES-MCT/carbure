from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from traceability.models import Action
from traceability.serializers.fields import LookupSlugRelatedField


class ConsumptionSerializer(serializers.ModelSerializer):
    type = serializers.HiddenField(default=Action.INIT)
    material = LookupSlugRelatedField(
        slug_field="name",
        lookup="material",
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": _("Matière inconnue")},
    )
    certificate = LookupSlugRelatedField(
        slug_field="certificate_id",
        lookup="certificate",
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": _("Certificat inconnu")},
    )
    site = LookupSlugRelatedField(
        slug_field="name",
        lookup="site",
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": _("Site inconnu")},
    )

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
