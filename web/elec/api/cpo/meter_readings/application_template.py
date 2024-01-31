from datetime import date
from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import UserRights
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.api.cpo.meter_readings.check_application import get_application_quarter
from elec.services.create_meter_reading_excel import create_meter_readings_data, create_meter_readings_excel


class ApplicationTemplateForm(forms.Form):
    quarter = forms.IntegerField(required=False)
    year = forms.IntegerField(required=False)


class ApplicationTemplateError:
    TOO_LATE = "TOO_LATE"
    NO_CHARGE_POINT_AVAILABLE = "NO_CHARGE_POINT_AVAILABLE"


@require_GET
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def get_application_template(request, entity):
    form = ApplicationTemplateForm(request.GET)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    auto_quarter, auto_year = get_application_quarter(date.today())
    quarter = form.cleaned_data["quarter"] or auto_quarter
    year = form.cleaned_data["year"] or auto_year

    if not quarter or not year:
        message = "Les inscriptions de relevés pour un trimestre doivent être réalisées entre les 10 derniers jours de la fin de ce trimestre et les 20 premiers jours du trimestre suivant."
        return ErrorResponse(400, ApplicationTemplateError.TOO_LATE, message=message)

    charge_points = ChargePointRepository.get_registered_charge_points(entity)

    if charge_points.count() == 0:
        message = "Le fichier excel n'a pas pu être généré car aucun point de recharge n'a été validé jusqu'à présent. Assurez-vous qu'au moins l'un de vos dossiers d'inscription de point de recharge a déjà été validé par la DGEC."
        return ErrorResponse(400, ApplicationTemplateError.NO_CHARGE_POINT_AVAILABLE, message=message)

    previous_application = MeterReadingRepository.get_previous_application(entity, quarter, year)
    meter_reading_data = create_meter_readings_data(charge_points, previous_application)

    file_name = f"meter_reading_template_Q{quarter}_{year}"
    excel_file = create_meter_readings_excel(file_name, quarter, year, meter_reading_data)
    return ExcelResponse(excel_file)
