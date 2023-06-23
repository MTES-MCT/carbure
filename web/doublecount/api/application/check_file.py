# /api/v5/stats/entity
import traceback
import datetime
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_admin_rights, check_user_rights
from core.models import UserRights
from doublecount.helpers import check_dc_file


class CheckFileError:
    MISSING_FILE = "MISSING_FILE"
    DOUBLE_COUNTING_IMPORT_FAILED = "DOUBLE_COUNTING_IMPORT_FAILED"
    FILE_CHECK_FAILED = "FILE_CHECK_FAILED"


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def check_file(request, *args, **kwargs):
    file = request.FILES.get("file")

    if file is None:
        return ErrorResponse(400, CheckFileError.MISSING_FILE)

    try:
        info, errors, sourcing_data, production_data = check_dc_file(file)
        error_count = (
            # len(errors["sourcing_history"])
            +len(errors["sourcing_forecast"])
            + len(errors["production"])
            + len(errors["global"])
        )

        file_info = {
            "file_name": file.name,
            "errors": errors,
            "error_count": error_count,
            "year": info["year"] or 0,
            "production_site": info["production_site"],
            "producer_email": info["producer_email"],
            "production": production_data,
            "sourcing": sourcing_data,
        }

        return SuccessResponse({"file": file_info, "checked_at": datetime.datetime.now().isoformat()})
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CheckFileError.FILE_CHECK_FAILED)
