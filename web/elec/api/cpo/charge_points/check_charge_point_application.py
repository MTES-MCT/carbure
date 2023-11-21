import traceback
from django.http import HttpRequest

from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.services.download_charge_point_data import download_charge_point_data
from elec.services.parse_charge_point_excel import parse_charge_point_excel


class CheckChargePointApplicationError:
    MISSING_FILE = "MISSING_FILE"
    CPO_ONLY = "CPO_ONLY"
    APPLICATION_FAILED = "APPLICATION_FAILED"
    MISSING_CHARGING_POINT_IN_DATAGOUV = "MISSING_CHARGING_POINT_IN_DATAGOUV"
    MISSING_CHARGING_POINT_DATA = "MISSING_CHARGING_POINT_DATA"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def check_charge_point_application(request: HttpRequest, *args, **kwargs):
    excel_file = request.FILES.get("file")
    entity_id = request.POST.get("entity_id")

    if not excel_file:
        return ErrorResponse(400, CheckChargePointApplicationError.MISSING_FILE)

    try:
        entity = Entity.objects.get(pk=entity_id, entity_type=Entity.CPO)
    except:
        traceback.print_exc()
        return ErrorResponse(400, CheckChargePointApplicationError.CPO_ONLY)

    try:
        excel_data = parse_charge_point_excel(excel_file)
        transport_data = download_charge_point_data()
        transport_data_index = {row["charge_point_id"]: row for row in transport_data}

        missing_data_gouv_charge_points = []
        invalid_charge_points = []
        charge_points = []

        for data in excel_data:
            charge_point_transport_data = transport_data_index.get(data["charge_point_id"], {})

            if len(charge_point_transport_data) == 0:
                missing_data_gouv_charge_points.append(data["charge_point_id"])

            # @TODO validate field values

            # create model instance and link it with the application
            charge_point = {**charge_point_transport_data, **data}

            charge_points.append(charge_point)

        print(charge_points)

        data = {"file_name": excel_file.name, "charging_point_count": len(charge_points), "errors": [], "error_count": 0}

        if len(missing_data_gouv_charge_points + invalid_charge_points) > 0:
            data["errors"] = create_errors(missing_data_gouv_charge_points, invalid_charge_points)
            data["error_count"] = len(data["errors"])
            return ErrorResponse(400, CheckChargePointApplicationError.APPLICATION_FAILED, data)

        return SuccessResponse(data)

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CheckChargePointApplicationError.APPLICATION_FAILED)


def create_errors(missing_data_gouv_charge_points, invalid_charge_points):
    errors = []
    # if len(missing_data_gouv_charge_points) > 0:
    #     errors.append(
    #         {
    #             "error": CheckChargePointApplicationError.MISSING_CHARGING_POINT_IN_DATAGOUV,
    #             "meta": missing_data_gouv_charge_points,
    #         }
    #     )
    if len(invalid_charge_points) > 0:
        errors.append(
            {
                "error": CheckChargePointApplicationError.MISSING_CHARGING_POINT_DATA,
                "meta": invalid_charge_points,
            }
        )
    return errors
