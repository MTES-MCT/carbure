from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.serializers import check_fields_required_when
from traceability.models import Action
from traceability.serializers.action import ActionExcelImportSerializer

TRANSPORT_FIELDS = ("shipping_method", "shipping_distance", "shipping_date", "etd1")
SHIPPING_FUEL_TYPES = (
    "Diesel B7",
    "B100",
    "HVO",
    "BioGNV",
    "GNV",
    "Électrique",
    "Hydrogène",
    "Non applicable",
)


def _not_consumed_on_production_site(attrs):
    return attrs.get("consumed_on_production_site") == "Non"


def _road_transport_off_site(attrs):
    return _not_consumed_on_production_site(attrs) and attrs.get("shipping_method") == Action.ROAD


class H2ActionExcelImportSerializer(ActionExcelImportSerializer):
    """H2 Excel extras: validated then discarded, not stored on Action."""

    lot_id = serializers.CharField(write_only=True)
    lot_quantity = serializers.DecimalField(max_digits=13, decimal_places=3, min_value=Decimal("0"), write_only=True)
    producer = serializers.CharField(write_only=True)
    consumed_on_production_site = serializers.ChoiceField(
        choices=["Oui", "Non"],
        write_only=True,
        error_messages={"invalid_choice": _("La valeur doit être Oui ou Non.")},
    )
    etd1 = serializers.DecimalField(
        max_digits=7, decimal_places=3, min_value=Decimal("0"), required=False, allow_null=True, write_only=True
    )
    etd2 = serializers.DecimalField(max_digits=7, decimal_places=3, min_value=Decimal("0"), write_only=True)
    shipping_fuel_type = serializers.ChoiceField(
        choices=SHIPPING_FUEL_TYPES,
        required=False,
        allow_null=True,
        allow_blank=True,
        write_only=True,
        error_messages={"invalid_choice": _("La valeur doit être l'une des options proposées.")},
    )

    class Meta(ActionExcelImportSerializer.Meta):
        fields = [
            *ActionExcelImportSerializer.Meta.fields,
            "lot_id",
            "lot_quantity",
            "producer",
            "consumed_on_production_site",
            "etd1",
            "etd2",
            "shipping_fuel_type",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        check_fields_required_when(
            attrs,
            [
                (_not_consumed_on_production_site, TRANSPORT_FIELDS),
                (_road_transport_off_site, ("shipping_fuel_type",)),
            ],
        )
        etd1 = attrs.pop("etd1", None) or Decimal("0")
        attrs["etd"] = etd1 + attrs.pop("etd2")
        return attrs
