from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import ExternalAdminRights
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationDetailsSerializer
from elec.services.create_meter_reading_excel import create_meter_readings_data, create_meter_readings_excel
from elec.services.export_charge_point_excel import export_charge_points_sample_to_excel
from elec.services.extract_audit_sample import extract_audit_sample


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=MeterReadingRepository.get_annotated_applications())
    percentage = forms.IntegerField(required=False)
    export = forms.BooleanField(required=False)
    sample = forms.BooleanField(required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application: ElecMeterReadingApplication = form.cleaned_data["application_id"]
    percentage = (form.cleaned_data["percentage"] or 10) / 100
    export = form.cleaned_data["export"]
    want_sample = form.cleaned_data["sample"]

    charge_points = ChargePointRepository.get_registered_charge_points(application.cpo)
    previous_application = MeterReadingRepository.get_previous_application(application.cpo, application.quarter, application.year)  # fmt:skip
    meter_readings = MeterReadingRepository.get_application_meter_readings(application.cpo, application)

    meter_readings_data = create_meter_readings_data(charge_points, previous_application, meter_readings)

    if export:
        if want_sample:
            application_charge_points = MeterReadingRepository.get_application_charge_points(application.cpo, application)
            random_charge_points = extract_audit_sample(application_charge_points, percentage)
            excel_file = export_charge_points_sample_to_excel(random_charge_points, application.cpo)
        else:
            file_name = f"meter_readings_{application.cpo.slugify()}_Q{application.quarter}_{application.year}"
            excel_file = create_meter_readings_excel(file_name, application.quarter, application.year, meter_readings_data)  # fmt:skip
        return ExcelResponse(excel_file)

    meter_readings_application = ElecMeterReadingApplicationDetailsSerializer(application).data

    return SuccessResponse(meter_readings_application)
