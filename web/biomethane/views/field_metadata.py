from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from biomethane.permissions import ReadAccessBiomethane
from biomethane.services.field_metadata import build_field_metadata_response_schema, get_verbose_fields_by_model

FIELD_METADATA_RESPONSE_SCHEMA = build_field_metadata_response_schema()


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            required=True,
            description="Authorised entity ID.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=FIELD_METADATA_RESPONSE_SCHEMA,
            description="Mapping des noms de champs vers leur verbose_name, par modèle biométhane.",
        )
    },
)
@api_view(["GET"])
@permission_classes([ReadAccessBiomethane])
def get_field_metadata(_):
    return Response(get_verbose_fields_by_model())
