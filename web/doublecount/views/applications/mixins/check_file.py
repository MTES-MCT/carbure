# /api/stats/entity
import datetime

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from doublecount.helpers import check_dc_file, check_has_dechets_industriels

from .response_serializer import CheckFileResponseSerializer


class CheckFilesError:
    MISSING_FILES = "MISSING_FILES"
    DOUBLE_COUNTING_IMPORT_FAILED = "DOUBLE_COUNTING_IMPORT_FAILED"
    FILE_CHECK_FAILED = "FILE_CHECK_FAILED"


class CheckFileActionMixin:
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
        request={
            "multipart/form-data": {"type": "object", "properties": {"file": {"type": "string", "format": "binary"}}},
        },
        responses=CheckFileResponseSerializer,
    )
    @action(methods=["post"], detail=False, url_path="check-file")
    def check_file(self, request, *args, **kwargs):
        file = request.FILES.get("file")

        if file is None:
            return Response(
                {"message": CheckFilesError.MISSING_FILES},
                status=status.HTTP_400_BAD_REQUEST,
            )

        (
            info,
            errors,
            sourcing_data,
            production_data,
            sourcing_history_data,
            production_history_data,
        ) = check_dc_file(file)

        error_count = (
            +len(errors["sourcing_forecast"])
            + len(errors["production"])
            + len(errors["global"])
            + len(errors["production_history"])
            + len(errors["sourcing_history"])
        )

        has_dechets_industriels = check_has_dechets_industriels(production_data)

        file_info = {
            "has_dechets_industriels": has_dechets_industriels,
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

        return Response({"file": file_info, "checked_at": datetime.datetime.now().isoformat()})
