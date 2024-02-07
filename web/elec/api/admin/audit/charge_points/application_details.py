import datetime
from math import e
from pprint import pprint
import random
from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import Entity, ExternalAdminRights
from elec.api.cpo.charge_points import application_details
from elec.models import ElecChargePoint
from elec.models import ElecChargePointApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.serializers.elec_charge_point_application import (
    ElecChargePointApplicationDetailsSerializer,
    ElecChargePointApplicationSerializer,
)
from elec.services.export_charge_point_excel import export_charge_points_sample_to_excel, export_charge_points_to_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ChargePointRepository.get_annotated_applications())
    export = forms.BooleanField(required=False)
    sample = forms.BooleanField(required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    export = form.cleaned_data["export"]
    want_sample = form.cleaned_data["sample"]

    if export:
        charge_points = ElecChargePoint.objects.filter(application=application.id)
        if want_sample:
            percentage = 0.10
            count_to_fetch = int(len(charge_points) * percentage)
            # Mélanger aléatoirement les charge_points
            random_charge_points = random.sample(list(charge_points), max(count_to_fetch, 1))
            # Conserver l'ordre d'origine en utilisant le slice
            charge_points = charge_points.filter(id__in=[cp.id for cp in random_charge_points])
            excel_file = export_charge_points_sample_to_excel(random_charge_points, application.cpo)
        else:
            excel_file = export_charge_points_to_excel(charge_points, application.cpo)
        return ExcelResponse(excel_file)

    charge_point_application = ElecChargePointApplicationDetailsSerializer(
        application
    ).data  # TODO envoyer liste des admins plutot que le premier

    return SuccessResponse(charge_point_application)
