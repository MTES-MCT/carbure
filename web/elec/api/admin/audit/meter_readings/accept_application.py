from django import forms
from django.http import HttpRequest

from django.views.decorators.http import require_POST
import pandas as pd
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights
from elec.api.cpo import meter_readings
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from entity.api import certificates


class AcceptApplicationForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ElecMeterReadingApplication.objects.all())
    force_validation = forms.BooleanField(required=False)


class AcceptApplicationError:
    AUDIT_NOT_STARTED = "AUDIT_NOT_STARTED"
    ALREADY_CHECKED = "ALREADY_CHECKED"


@require_POST
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def accept_application(request: HttpRequest):
    form = AcceptApplicationForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    force_validation = form.cleaned_data["force_validation"]

    if (
        application.status != ElecMeterReadingApplication.PENDING
        and application.status != ElecMeterReadingApplication.AUDIT_IN_PROGRESS
    ):
        return ErrorResponse(400, AcceptApplicationError.ALREADY_CHECKED, "Application has already been checked by admin")

    if application.status == ElecMeterReadingApplication.PENDING and not force_validation:
        return ErrorResponse(
            400, AcceptApplicationError.AUDIT_NOT_STARTED, "Application cannot be accepted if audit is not started"
        )

    # creer un ElecProvisionCertificate groupant tous les meter readings par charge_poing.operating_unit

    ## recuperer tous les MEterReadings de la demande
    meter_readings = ElecMeterReading.objects.filter(application=application)
    data = [
        {
            "renewable_energy": meter_reading.renewable_energy,
            "operating_unit": meter_reading.charge_point.charge_point_id[:5],  # Inclure le charge_point_id
        }
        for meter_reading in meter_readings
    ]

    ## convertir en dataframe et grouper par operating_unit et sommer les extracted_energy
    meter_readings_df = pd.DataFrame(data)
    meter_readings_df_grouped = meter_readings_df.groupby("operating_unit").agg({"renewable_energy": "sum"}).reset_index()

    ## créer les ElecProvisionCertificate à partir des groupes
    certificate_model_instances = []
    for group in meter_readings_df_grouped.to_dict(orient="records"):

        certif = ElecProvisionCertificate(
            cpo=application.cpo,
            quarter=application.quarter,
            year=application.year,
            operating_unit=group["operating_unit"],
            energy_amount=group["renewable_energy"],
            current_type=ElecChargePoint.DC,
            remaining_energy_amount=group["renewable_energy"],
        )
        certificate_model_instances.append(certif)
    ElecProvisionCertificate.objects.bulk_create(certificate_model_instances)

    application.status = ElecChargePointApplication.ACCEPTED
    application.save()

    return SuccessResponse()
