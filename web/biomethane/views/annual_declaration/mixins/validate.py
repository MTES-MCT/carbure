from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models import BiomethaneAnnualDeclaration


class ValidateActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        request=None,
        responses={
            200: None,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="validate",
    )
    def validate_annual_declaration(self, request, *args, **kwargs):
        try:
            declaration = self.get_queryset().get()
            declaration.status = BiomethaneAnnualDeclaration.DECLARED
            declaration.save(update_fields=["status"])

            return Response(status=status.HTTP_200_OK)
        except BiomethaneAnnualDeclaration.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
