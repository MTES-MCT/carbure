from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Entity, UserRights
from core.permissions import HasUserRights
from solid_biomass.models import EnergyInstallation
from solid_biomass.serializers.energy_installation import EnergyInstallationSerializer


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
