# /api/stats/entity
import datetime
import traceback

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from doublecount.helpers import check_dc_file

from .response_serializer import CheckFileResponseSerializer


class CheckFilesError:
    MISSING_FILES = "MISSING_FILES"
    DOUBLE_COUNTING_IMPORT_FAILED = "DOUBLE_COUNTING_IMPORT_FAILED"
    FILE_CHECK_FAILED = "FILE_CHECK_FAILED"


class CheckAdminFileSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField())


class CheckAdminFilesActionMixin:
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
        request=CheckAdminFileSerializer,
        responses=CheckFileResponseSerializer(many=True),
    )
    @action(methods=["post"], detail=False, url_path="check-admin-files")
    def check_admin_files(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")

        if len(files) == 0:
            return Response(
                {"message": CheckFilesError.MISSING_FILES},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_infos = []
            for file in files:
                info, errors, sourcing_data, production_data, sourcing_history_data, production_history_data = check_dc_file(
                    file
                )
                error_count = +len(errors["sourcing_forecast"]) + len(errors["production"]) + len(errors["global"])

                file_infos.append(
                    {
                        "file_name": file.name,
                        "errors": errors,
                        "error_count": error_count,
                        "start_year": info["start_year"] or 0,
                        "production_site": info["production_site"],
                        "producer_email": info["producer_email"],
                        "production": production_data,
                        "sourcing": sourcing_data,
                        "sourcing_history": sourcing_history_data,
                        "production_history": production_history_data,
                    }
                )

            return Response({"files": file_infos, "checked_at": datetime.datetime.now().isoformat()})
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": CheckFilesError.FILE_CHECK_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )
