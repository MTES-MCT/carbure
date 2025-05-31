import traceback

from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core import private_storage

from .response_serializer import ResponseSerializer


class UpdateIndustrialWastesFileSerializer(serializers.Serializer):
    industrial_wastes_file = serializers.FileField(required=False)


class UpdateIndustrialWastesFileActionMixin:
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
        request=UpdateIndustrialWastesFileSerializer,
        responses={200: ResponseSerializer},
        examples=[
            OpenApiExample(
                "Example of response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=True, url_path="update-industrial-wastes-file")
    @transaction.atomic
    def update_industrial_wastes_file(self, request, id=None):
        application = self.get_object()
        has_dechets_industriels = application.has_dechets_industriels()

        if not has_dechets_industriels:
            return Response(
                {"status": "error", "message": "Application doesn't declare any industrial wastes"},
                status=400,
            )

        serializer = UpdateIndustrialWastesFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        industrial_wastes_file = serializer.validated_data.get("industrial_wastes_file")

        print("-----")
        print(serializer.validated_data)
        print(industrial_wastes_file)
        print("-----")

        s3_path_industrial_wastes_file = f"doublecounting/{application.id}_industrial_wastes_file.pdf"

        try:
            application.industrial_wastes_file_link = s3_path_industrial_wastes_file
            application.save()
            private_storage.save(s3_path_industrial_wastes_file, industrial_wastes_file)
        except Exception:
            traceback.print_exc()

        return Response({"status": "success"})
