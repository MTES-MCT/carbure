# /api/v5/stats/entity
import traceback
import datetime
from core.common import SuccessResponse, ErrorResponse
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
            info, errors, sourcing_data, production_data = check_dc_file(file)
            print("info: ", info)
            error_count = (
                # len(errors["sourcing_history"])
                +len(errors["sourcing_forecast"])
                + len(errors["production"])
                + len(errors["global"])
            )

            print('info["producer_email"]: ', info["producer_email"])
            file_infos.append(
                {
                    "file_name": file.name,
                    "errors": errors,
                    "error_count": error_count,
                    "year": info["year"] or 0,
                    "production_site": info["production_site"],
                    "producer_email": info["producer_email"],
                    "production": production_data,
                    "sourcing": sourcing_data,
                }
            )

        return SuccessResponse({"files": file_infos, "checked_at": datetime.datetime.now().isoformat()})
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CheckFilesError.FILE_CHECK_FAILED)
