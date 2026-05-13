from calendar import monthrange
from datetime import date

from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from tiruert.filters.mac import MacFilter
from tiruert.models import MacFossilFuel
from tiruert.serializers import MacFossilFuelInputSerializer, MacFossilFuelSerializer
from tiruert.services.declaration_period import DeclarationPeriodService


class ReplaceActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Authorised entity ID.",
                required=True,
            ),
            OpenApiParameter(
                name="year",
                type=int,
                location=OpenApiParameter.QUERY,
                description="MAC year.",
                required=True,
            ),
        ],
        request=MacFossilFuelInputSerializer(many=True),
        responses=MacFossilFuelSerializer(many=True),
    )
    @action(detail=False, methods=["put"], url_path="replace")
    def replace(self, request, *args, **kwargs):
        serializer = MacFossilFuelInputSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        filterset = MacFilter(data=request.query_params)
        if not filterset.is_valid():
            raise ValidationError(filterset.errors)

        year = int(filterset.form.cleaned_data["year"])
        declaration_year = DeclarationPeriodService.get_current_declaration_year()

        if year != declaration_year:
            raise ValidationError({"year": "MACs can only be modified for the currently active declaration year"})

        macs = serializer.validated_data

        with transaction.atomic():
            MacFossilFuel.objects.filter(operator=request.entity, year=year).delete()
            MacFossilFuel.objects.bulk_create(
                [
                    MacFossilFuel(
                        operator=request.entity,
                        fuel=mac["fuel"],
                        volume=mac["volume"],
                        period=(year * 100) + mac["month"],
                        year=year,
                        start_date=date(year, mac["month"], 1),
                        end_date=date(year, mac["month"], monthrange(year, mac["month"])[1]),
                    )
                    for mac in macs
                ]
            )

        queryset = self.filter_queryset(self.get_queryset())
        output_serializer = self.get_serializer(queryset, many=True)
        return Response(output_serializer.data)
