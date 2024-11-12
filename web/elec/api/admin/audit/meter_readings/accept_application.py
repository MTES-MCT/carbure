import pandas as pd
from django import forms
from django.conf import settings
from django.db.models import Sum
from django.http import HttpRequest
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.helpers import send_mail
from core.models import ExternalAdminRights
from core.utils import CarbureEnv
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.models.elec_provision_certificate import ElecProvisionCertificate


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

    if application.status in (ElecMeterReadingApplication.ACCEPTED, ElecMeterReadingApplication.REJECTED):
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
            energy_amount=group["renewable_energy"] / 1000,
            current_type=ElecProvisionCertificate.METER_READINGS,
            remaining_energy_amount=group["renewable_energy"] / 1000,
        )
        certificate_model_instances.append(certif)
    ElecProvisionCertificate.objects.bulk_create(certificate_model_instances)

    application.status = ElecChargePointApplication.ACCEPTED
    application.save()

    # marque l'échantillon comme "audité"
    audit_sample = application.audit_sample.first()
    if audit_sample:
        audit_sample.status = ElecAuditSample.AUDITED
        audit_sample.save()

    send_email_to_cpo(application, request)

    return SuccessResponse()


def send_email_to_cpo(application: ElecMeterReadingApplication, request: HttpRequest):
    quarter = f"T{application.quarter} {application.year}"
    total_energy = round(application.elec_meter_readings.aggregate(total_energy=Sum("renewable_energy"))["total_energy"], 2)
    meter_reading_count = application.elec_meter_readings.count()
    meter_reading_link = f"{CarbureEnv.get_base_url()}/org/{application.cpo.pk}/elec/{application.year}/provisioned"

    text_message = f"""
    Bonjour,

    La DGEC vient de valider votre relevé trimestriel {quarter} pour les {meter_reading_count} points de recharge renseignés.
    {total_energy} kWh renouvelable vous ont été versés sous forme de certificat de fourniture dans votre espace Carbure visible sur <a href="{meter_reading_link}">ce lien</a>.

    Merci beaucoup

    Bien cordialement,
    L'équipe CarbuRe
    """  # noqa: E501

    send_mail(
        request=request,
        subject=f"[CarbuRe] Relevés {quarter} validés",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["carbure@beta.gouv.fr"],
    )
