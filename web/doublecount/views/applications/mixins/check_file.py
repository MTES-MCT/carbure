# /api/stats/entity
import datetime
import traceback

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from doublecount.helpers import check_dc_file

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

        try:
            info, errors, sourcing_data, production_data, sourcing_history_data = check_dc_file(file)
            error_count = +len(errors["sourcing_forecast"]) + len(errors["production"]) + len(errors["global"])

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
            }

            return Response({"file": file_info, "checked_at": datetime.datetime.now().isoformat()})
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": CheckFilesError.FILE_CHECK_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )


def check_has_dechets_industriels(production_data):
    if production_data is None:
        return False
    for row in production_data:
        if row["feedstock"]["code"] in ["DECHETS_INDUSTRIELS", "AMIDON_RESIDUEL_DECHETS"]:
            return True
    return False
