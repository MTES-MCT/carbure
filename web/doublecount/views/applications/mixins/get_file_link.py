from django.core.files.storage import default_storage
from django.http import HttpResponse
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.decorators import action

from .response_serializer import LinkResponseSerializer


class GetLinkActionMixin:
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
        responses={200: LinkResponseSerializer},
        examples=[
            OpenApiExample(
                "Example of response.",
                value={"link": "https://foobar.s3.amazonaws.com/exports/FR_126_2024.docx?...."},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["get"], detail=True, url_path="get-link")
    def get_link(self, request, id=None):
        application = self.get_object()

        file_key = f"application/exports/{application.id}/{application.certificate_id}.docx"

        try:
            with default_storage.open(file_key, "rb") as file:
                response = HttpResponse(
                    file.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                response["Content-Disposition"] = f"attachment; filename={file_key.split('/')[-1]}"
                return response
        except Exception as e:
            return HttpResponse(f"Erreur lors du téléchargement : {e}", status=500)
