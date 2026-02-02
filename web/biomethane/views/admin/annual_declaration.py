from django.db.models import Q
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.permissions import HasDrealRights
from biomethane.serializers.admin.annual_declaration import BiomethaneAdminAnnualDeclarationSerializer
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity


class BiomethaneAdminAnnualDeclarationViewSet(GenericViewSet, ListModelMixin):
    """Liste des déclarations annuelles des producteurs de biométhane pour l'année courante (vue DREAL)."""

    queryset = BiomethaneAnnualDeclaration.objects.all()
    permission_classes = [HasDrealRights]
    serializer_class = BiomethaneAdminAnnualDeclarationSerializer

    def list(self, request, *args, **kwargs):
        entity = request.entity
        year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        accessible_dept_codes = list(entity.get_accessible_departments().values_list("code_dept", flat=True))

        entities = (
            Entity.objects.filter(
                entity_type=Entity.BIOMETHANE_PRODUCER,
            )
            .filter(
                Q(biomethane_production_unit__department__code_dept__in=accessible_dept_codes)
                # | Q(registered_zipcode__in=accessible_dept_codes)
            )
            .values_list("pk", flat=True)
        )

        declarations = (
            BiomethaneAnnualDeclaration.objects.filter(producer_id__in=entities, year=year)
            .select_related(
                "producer",
                "producer__biomethane_contract",
                "producer__biomethane_production_unit__department",
            )
            .order_by("producer__name")
        )

        serializer = self.get_serializer(declarations, many=True)
        return Response(serializer.data)
