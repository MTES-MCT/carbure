from rest_framework import serializers

_GES_DECIMAL = {"max_digits": 13, "decimal_places": 3, "read_only": True}


class ActionTotalEmissionsSerializer(serializers.Serializer):
    """Cumulative GES along the parent chain (gCO₂eq/MJ)."""

    eec = serializers.DecimalField(**_GES_DECIMAL)
    el = serializers.DecimalField(**_GES_DECIMAL)
    ei = serializers.DecimalField(**_GES_DECIMAL)
    ep = serializers.DecimalField(**_GES_DECIMAL)
    etd = serializers.DecimalField(**_GES_DECIMAL)
    eu = serializers.DecimalField(**_GES_DECIMAL)
    eccs = serializers.DecimalField(**_GES_DECIMAL)
    esca = serializers.DecimalField(**_GES_DECIMAL)
    eccr = serializers.DecimalField(**_GES_DECIMAL)
    total = serializers.DecimalField(**_GES_DECIMAL)
