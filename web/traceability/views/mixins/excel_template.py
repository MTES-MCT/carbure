from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse
from traceability.services.action_excel import build_action_import_template


class ExcelTemplateActionMixin:
    @extend_schema(
        operation_id="download_actions_import_template",
        description="Download the action import Excel template for the given industry.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="Generated Excel file",
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="import/template")
    def download_import_template(self, request, *args, **kwargs):
        return ExcelResponse(build_action_import_template(request.handler))
