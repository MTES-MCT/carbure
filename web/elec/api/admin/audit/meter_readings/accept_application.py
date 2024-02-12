from django import forms
from django.http import HttpRequest

from django.views.decorators.http import require_POST
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights
from elec.models.elec_charge_point_application import ElecChargePointApplication
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

    # recuperer tous les MEterReadings de l'application
    # creer un ElecProvisionCertificate groupant tous les meter readings par operating_unit

    # charge_point_id          charge_point_data["operating_unit"] = charge_point_data["charge_point_id"].str[:5]
    # for record in certificate_df.to_dict("records"):
    #     current_type = ElecChargePoint.AC if record["current_type"] == "AC" else ElecChargePoint.DC
    #     certif = ElecProvisionCertificate(
    #         cpo=cpos_by_name.get(normalize_string(record["cpo"])),
    #         quarter=record["quarter"],
    #         year=record["year"],
    #         operating_unit=record["operating_unit"],
    #         energy_amount=record["energy_amount"],
    #         current_type=current_type,
    #         remaining_energy_amount=record["energy_amount"],
    #     )
    #     certificate_model_instances.append(certif)
    # try:
    #     ElecProvisionCertificate.objects.bulk_create(certificate_model_instances)
    # except:
    #     traceback.print_exc()
    #     return ErrorResponse(400, CertificateImportError.DB_INSERTION_ERROR, "Error during data insert")

    application.status = ElecChargePointApplication.ACCEPTED
    application.save()

    return SuccessResponse()
