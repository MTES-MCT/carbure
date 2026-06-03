from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.serializers.supply_plan.tariff_coefficient_proportions import TariffCoefficientProportionsSerializer


class TariffCoefficientProportionsActionMixin:
    @extend_schema(responses={200: TariffCoefficientProportionsSerializer})
    @action(
        detail=False,
        methods=["get"],
        url_path="tariff-coefficient-proportions",
    )
    def tariff_coefficient_proportions(self, request, *args, **kwargs):
        """Volume-weighted P1/P2/P3/P/Pef shares for the filtered supply plan inputs."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
