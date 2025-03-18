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
from elec.services.create_meter_reading_excel import create_meter_readings_excel
from elec.services.meter_readings_application_quarter import get_application_quarter


class ApplicationTemplateForm(forms.Form):
    quarter = forms.IntegerField(required=False)
    year = forms.IntegerField(required=False)


class ApplicationTemplateError:
    TOO_LATE = "TOO_LATE"
    NO_CHARGE_POINT_AVAILABLE = "NO_CHARGE_POINT_AVAILABLE"
    ONLY_ARTICLE_2_CHARGE_POINTS = "ONLY_ARTICLE_2_CHARGE_POINTS"


@require_GET
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def get_application_template(request, entity):
    form = ApplicationTemplateForm(request.GET)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    today = date.today()
    auto_year, auto_quarter = get_application_quarter(today)
    quarter = form.cleaned_data["quarter"] or auto_quarter
    year = form.cleaned_data["year"] or auto_year

    if not quarter or not year:
        message = "Les inscriptions de relevés pour un trimestre doivent être réalisées entre les 10 derniers jours de ce trimestre et les 20 premiers jours du trimestre suivant."  # noqa: E501
        return ErrorResponse(400, ApplicationTemplateError.TOO_LATE, message=message)

    charge_points = ChargePointRepository.get_registered_charge_points(entity).filter(is_article_2=False)

    if charge_points.count() == 0:
        message = "Le fichier excel n'a pas pu être généré car aucun point de recharge n'a été validé jusqu'à présent. Assurez-vous qu'au moins l'un de vos dossiers d'inscription de point de recharge a déjà été validé par la DGEC."  # noqa: E501
        return ErrorResponse(400, ApplicationTemplateError.NO_CHARGE_POINT_AVAILABLE, message=message)

    charge_points = MeterReadingRepository.annotate_charge_points_with_latest_readings(charge_points, today)

    meter_reading_data = []
    for charge_point in charge_points:
        meter_reading_data.append(
            {
                "charge_point_id": charge_point.charge_point_id,
                "previous_reading": charge_point.latest_reading_index,
                "current_reading": None,
                "reading_date": None,
            }
        )

    file_name = f"meter_reading_template_Q{quarter}_{year}"
    excel_file = create_meter_readings_excel(file_name, quarter, year, meter_reading_data)
    return ExcelResponse(excel_file)
