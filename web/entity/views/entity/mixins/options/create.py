from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ValidationError

from biomethane.models import BiomethaneProductionUnit
from core.models import Department, Entity, ExternalAdminRights
from transactions.models import Site


class CreateEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ENTITY_EXISTS = "ENTITY_EXISTS"
    ENTITY_CREATION_FAILED = "ENTITY_CREATION_FAILED"


ENTITY_CREATE_FIELDS = ["name", "entity_type", "has_saf", "has_elec"]
PRODUCTION_UNIT_CREATE_FIELDS = ["company_address", "postal_code", "city", "department", "insee_code"]


class CreateEntitySerializer(ModelSerializer):
    """Champs optionnels pour création d'une unité de production (DREAL uniquement)."""

    company_address = serializers.CharField(required=False, allow_blank=True, max_length=256)
    postal_code = serializers.CharField(required=False, allow_blank=True, max_length=32)
    city = serializers.CharField(required=False, allow_blank=True, max_length=128)
    department = serializers.CharField(required=False, allow_blank=True, max_length=3)
    insee_code = serializers.CharField(required=False, allow_blank=True, max_length=5)

    class Meta:
        model = Entity
        fields = ENTITY_CREATE_FIELDS + PRODUCTION_UNIT_CREATE_FIELDS

    def validate_name(self, value):
        if Entity.objects.filter(name=value).exists():
            raise ValidationError(CreateEntityError.ENTITY_EXISTS)
        return value


def _should_create_production_unit(request):
    """True si l'entité courante est EXTERNAL_ADMIN avec droit DREAL."""
    entity = getattr(request, "entity", None)
    if not entity:
        return False
    return entity.entity_type == Entity.EXTERNAL_ADMIN and entity.has_external_admin_right(ExternalAdminRights.DREAL)


def _create_production_unit_for_entity(entity, validated_data):
    """Crée un BiomethaneProductionUnit pour l'entité avec les champs fournis."""
    department = None
    if validated_data.get("department"):
        department = Department.objects.filter(code_dept=validated_data["department"].strip()).first()

    BiomethaneProductionUnit.objects.create(
        producer=entity,
        site_type=Site.PRODUCTION_BIOGAZ,
        address=validated_data.get("company_address") or "",
        postal_code=validated_data.get("postal_code") or "",
        city=validated_data.get("city") or "",
        department=department,
        insee_code=validated_data.get("insee_code") or "",
    )


# ViewSet
class CreateEntityActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=CreateEntitySerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = CreateEntitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            entity_data = {k: validated_data[k] for k in ENTITY_CREATE_FIELDS}
            entity = Entity.objects.create(**entity_data)
            print("entity", entity)
            print("validated_data", validated_data)
            print("should create production unit", _should_create_production_unit(request))
            if _should_create_production_unit(request):
                _create_production_unit_for_entity(entity, validated_data)

            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {"message": CreateEntityError.ENTITY_CREATION_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )
