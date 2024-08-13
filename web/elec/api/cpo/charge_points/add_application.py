from pandas.core.frame import DataFrame
from django.http import HttpRequest
from django.db import transaction
from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models import ElecChargePoint, ElecChargePointApplication, ElecMeter
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.services.import_charge_point_excel import import_charge_point_excel


class AddChargePointApplicationError:
    MISSING_FILE = "MISSING_FILE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NO_CHARGE_POINT_DETECTED = "NO_CHARGE_POINT_DETECTED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def add_application(request: HttpRequest, entity: Entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, AddChargePointApplicationError.MISSING_FILE)

    charge_point_data, errors, original = import_charge_point_excel(excel_file)

    if len(errors) > 0:
        return ErrorResponse(400, AddChargePointApplicationError.VALIDATION_FAILED)

    if len(charge_point_data) == 0:
        return ErrorResponse(400, AddChargePointApplicationError.NO_CHARGE_POINT_DETECTED)

    new_charge_points = [cp["charge_point_id"] for cp in charge_point_data]
    replaced_charge_points = ChargePointRepository.get_replaced_charge_points(entity, new_charge_points)
    replaced_charge_points_by_id = replaced_charge_points.values_list("charge_point_id", flat=True)

    duplicate = False
    if isinstance(original, DataFrame):
        for _, row in original.iterrows():
            charge_point_id = row["charge_point_id"]
            if charge_point_id in replaced_charge_points_by_id:
                duplicate = True
                break

    if duplicate:
        return ErrorResponse(400, AddChargePointApplicationError.VALIDATION_FAILED)

    with transaction.atomic():
        replaced_applications = ElecChargePointApplication.objects.filter(
            cpo=entity, status__in=[ElecChargePointApplication.PENDING, ElecChargePointApplication.REJECTED]
        )

        # Delete older pending applications
        replaced_applications.delete()

        application = ElecChargePointApplication(cpo=entity)
        application.save()

        # We can't use a bulk_create here because we need the ID of each meter created to associate it to the right charge point
        meters = []
        for data in charge_point_data:
            meter = ElecMeter(
                mid_certificate=data.pop("mid_id"),
                initial_index=data.pop("measure_energy"),
                initial_index_date=data.pop("measure_date"),
                charge_point=None,
            )
            meter.save()
            meters.append(meter)

        # Prepare charge points to bulk create
        charge_points = [
            ElecChargePoint(
                **data,
                current_meter=meter,
                application=application,
                cpo=entity,
            )
            for data, meter in zip(charge_point_data, meters)
        ]
        ElecChargePoint.objects.bulk_create(charge_points)

        new_charge_points = ElecChargePoint.objects.filter(current_meter__in=meters).order_by("id")

        # Associate the right charge point to the right meter
        for meter, charge_point in zip(meters, new_charge_points):
            meter.charge_point = charge_point

        ElecMeter.objects.bulk_update(meters, ["charge_point"])

    return SuccessResponse()
