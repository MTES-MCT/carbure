# /api/stats/entity
import datetime
import traceback

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from doublecount.helpers import check_dc_file


class CheckFilesError:
    MISSING_FILES = "MISSING_FILES"
    DOUBLE_COUNTING_IMPORT_FAILED = "DOUBLE_COUNTING_IMPORT_FAILED"
    FILE_CHECK_FAILED = "FILE_CHECK_FAILED"


@check_admin_rights()
def check_files(request, *args, **kwargs):
    files = request.FILES.getlist("files")

    if len(files) == 0:
        return ErrorResponse(400, CheckFilesError.MISSING_FILES)

    try:
        file_infos = []
        for file in files:
            info, errors, sourcing_data, production_data, sourcing_history_data = check_dc_file(file)
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
                }
            )

        return SuccessResponse({"files": file_infos, "checked_at": datetime.datetime.now().isoformat()})
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CheckFilesError.FILE_CHECK_FAILED)
