# /api/v5/stats/entity
import traceback
import datetime
import unicodedata
import re
from django.db import transaction, IntegrityError
from doublecount.models import DoubleCountingAgreement
from core.common import CarbureException, SuccessResponse, ErrorResponse
from core.decorators import check_admin_rights
from doublecount.dc_sanity_checks import check_dc_globally, error, DoubleCountingError
from doublecount.dc_parser import parse_dc_excel
from doublecount.helpers import load_dc_sourcing_data, load_dc_production_data
from doublecount.serializers import DoubleCountingProductionSerializer, DoubleCountingSourcingSerializer


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
            error_count = (
                # len(errors["sourcing_history"])
                +len(errors["sourcing_forecast"])
                + len(errors["production"])
                + len(errors["global"])
            )

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


@transaction.atomic
def check_dc_file(file):
    try:
        directory = "/tmp"
        now = datetime.datetime.now()
        filename = "%s_%s.xlsx" % (now.strftime("%Y%m%d.%H%M%S"), file.name.upper())
        filename = "".join((c for c in unicodedata.normalize("NFD", filename) if unicodedata.category(c) != "Mn"))
        filepath = "%s/%s" % (directory, filename)

        # save file
        with open(filepath, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        info, sourcing_forecast, production_forecast = parse_dc_excel(filepath)
        # info, sourcing_history, sourcing_forecast, production_forecast = parse_dc_excel(filepath)

        # get dc period for upload
        years = [production["year"] for production in production_forecast]
        end_year = max(years) if len(years) > 0 else info["year"] + 1
        start = datetime.date(end_year - 1, 1, 1)
        end = datetime.date(end_year, 12, 31)

        # create temporary agreement to hold all the data that will be parsed
        dca = DoubleCountingAgreement(
            period_start=start,
            period_end=end,
        )

        # sourcing_history_data, sourcing_history_errors = load_dc_sourcing_data(
        #     dca, sourcing_history
        # )
        sourcing_forecast_data, sourcing_forecast_errors = load_dc_sourcing_data(dca, sourcing_forecast)
        production_data, production_errors = load_dc_production_data(dca, production_forecast)

        sourcing_data = sourcing_forecast_data

        # sourcing_data = sourcing_history_data + sourcing_forecast_data
        global_errors = check_dc_globally(sourcing_data, production_data)

        return (
            info,
            {
                # "sourcing_history": sourcing_history_errors,
                "sourcing_forecast": sourcing_forecast_errors,
                "production": production_errors,
                "global": global_errors,
            },
            DoubleCountingSourcingSerializer(sourcing_data, many=True).data,
            DoubleCountingProductionSerializer(production_data, many=True).data,
        )

    except CarbureException as e:
        if e.error == DoubleCountingError.BAD_WORKSHEET_NAME:
            excel_error = error(DoubleCountingError.BAD_WORKSHEET_NAME, is_blocking=True, meta=e.meta)

    except Exception as e:
        traceback.print_exc()

        # bad tab name
        sheetNameRegexp = r"'Worksheet (.*) does not exist.'"
        matchedSheet = re.match(sheetNameRegexp, str(e))
        if matchedSheet:
            sheetName = matchedSheet[1]
            excel_error = error(
                DoubleCountingError.BAD_WORKSHEET_NAME,
                is_blocking=True,
                meta={"sheet_name": sheetName},
            )
        elif str(e) == "year 0 is out of range":
            excel_error = error(DoubleCountingError.UNKNOWN_YEAR, is_blocking=True)
        else:
            excel_error = error(DoubleCountingError.EXCEL_PARSING_ERROR, is_blocking=True, meta=str(e))

    info = {"production_site": None, "year": 0}
    return (
        info,
        {
            "sourcing_forecast": [],
            # "sourcing_history": [],
            "production": [],
            "global": [excel_error],
        },
        None,
        None,
    )
