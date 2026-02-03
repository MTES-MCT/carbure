from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService


class ValidateActionMixin:
    @extend_schema(
        responses={
            status.HTTP_200_OK: None,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        request=None,
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="validate",
    )
    def validate_annual_declaration(self, request, *args, **kwargs):
        try:
            declaration = self.filter_queryset(self.get_queryset()).get()

            if BiomethaneAnnualDeclarationService.is_declaration_complete(declaration) and declaration.is_open:
                current_status = BiomethaneAnnualDeclarationService.get_declaration_status(declaration)
                if current_status == BiomethaneAnnualDeclaration.OVERDUE:
                    declaration.is_open = False

                declaration.status = BiomethaneAnnualDeclaration.DECLARED

                declaration.save(update_fields=["status", "is_open"])
                return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        except BiomethaneAnnualDeclaration.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
