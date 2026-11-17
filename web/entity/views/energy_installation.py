from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Entity, UserRights
from core.permissions import HasUserRights
from transactions.models import EnergyInstallation


class EnergyInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyInstallation
        fields = [
            "production_type",
            "heat_type",
            "commissioning_date",
            "useful_temperature",
            "electrical_efficiency",
            "thermal_efficiency",
            "icpe_number",
            "icpe_regime",
        ]

    def validate(self, attrs):
        production_type = attrs.get("production_type", getattr(self.instance, "production_type", None))
        if production_type not in (EnergyInstallation.HEAT, EnergyInstallation.COGENERATION):
            attrs["heat_type"] = None
        if production_type != EnergyInstallation.COGENERATION:
            attrs["useful_temperature"] = None
        if production_type not in (EnergyInstallation.ELECTRICITY, EnergyInstallation.COGENERATION):
            attrs["electrical_efficiency"] = None
        if production_type not in (EnergyInstallation.HEAT, EnergyInstallation.COGENERATION):
            attrs["thermal_efficiency"] = None
        return attrs


@extend_schema(parameters=[OpenApiParameter("entity_id", int, OpenApiParameter.QUERY, required=True)])
class EnergyInstallationView(APIView):
    def get_permissions(self):
        roles = [UserRights.ADMIN, UserRights.RW] if self.request.method == "PUT" else None
        return [HasUserRights(role=roles, entity_type=[Entity.SOLID_BIOMASS_ENERGY_PRODUCER])]

    @extend_schema(responses=EnergyInstallationSerializer)
    def get(self, request):
        installation = EnergyInstallation.objects.filter(producer=request.entity).first()
        return Response(EnergyInstallationSerializer(installation).data if installation else {})

    @extend_schema(request=EnergyInstallationSerializer, responses=EnergyInstallationSerializer)
    def put(self, request):
        installation = EnergyInstallation.objects.filter(producer=request.entity).first()
        serializer = EnergyInstallationSerializer(installation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if installation:
            serializer.save()
        else:
            serializer.save(producer=request.entity, name=request.entity.name)
        return Response(serializer.data, status=status.HTTP_200_OK)
