from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpRequest
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from core.utils import CarbureEnv
from elec.models.elec_audit_charge_point import ElecAuditChargePoint
from elec.models.elec_audit_sample import ElecAuditSample
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.elec_audit_repository import ElecAuditRepository
from elec.services.import_elec_audit_report_excel import import_elec_audit_report_excel


class AcceptReportForm(forms.Form):
    file = forms.FileField()
    audit_sample_id = forms.IntegerField()


class AcceptReportError:
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NO_CHARGE_POINT_DETECTED = "NO_CHARGE_POINT_DETECTED"


@require_POST
@check_user_rights(entity_type=[Entity.AUDITOR])
def accept_report(request: HttpRequest, entity: Entity):
    form = AcceptReportForm(request.POST, request.FILES)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    audit_sample_id = form.cleaned_data["audit_sample_id"]
    excel_file = form.cleaned_data["file"]

    audit_sample = ElecAuditRepository.get_audited_sample_by_id(request.user, audit_sample_id)

    if not audit_sample:
        return ErrorResponse(404, CarbureError.NOT_FOUND)

    audited_charge_points = audit_sample.audited_charge_points.select_related("charge_point").all()
    charge_point_reports, errors = import_elec_audit_report_excel(excel_file, audited_charge_points)

    if len(errors) == 0:
        reports_by_charge_point_id = {report["charge_point_id"]: report for report in charge_point_reports}

        updated_audited_charge_point = []
        for charge_point_audit in audited_charge_points:
            charge_point_id = charge_point_audit.charge_point.charge_point_id
            report = reports_by_charge_point_id.get(charge_point_id, {})
            for key in report:
                setattr(charge_point_audit, key, report[key])
            updated_audited_charge_point.append(charge_point_audit)

        with transaction.atomic():
            audit_sample.auditor = entity
            audit_sample.status = ElecAuditSample.AUDITED
            audit_sample.save()

            if audit_sample.charge_point_application:
                audit_sample.charge_point_application.status = ElecChargePointApplication.AUDIT_DONE
                audit_sample.charge_point_application.save()

            if audit_sample.meter_reading_application:
                audit_sample.meter_reading_application.status = ElecMeterReadingApplication.AUDIT_DONE
                audit_sample.meter_reading_application.save()

            ElecAuditChargePoint.objects.bulk_update(
                updated_audited_charge_point,
                [
                    "is_auditable",
                    "current_type",
                    "observed_mid_or_prm_id",
                    "observed_energy_reading",
                    "has_dedicated_pdl",
                    "audit_date",
                    "comment",
                ],
            )

    data = {}
    data["file_name"] = excel_file.name
    data["charge_point_count"] = len(charge_point_reports)
    data["errors"] = []
    data["error_count"] = 0

    if len(errors) > 0:
        data["errors"] = errors
        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, AcceptReportError.VALIDATION_FAILED, data)

    if len(charge_point_reports) == 0:
        data["errors"] = [{"error": "NO_CHARGE_POINT_DETECTED"}]
        data["error_count"] = 1
        return ErrorResponse(400, AcceptReportError.NO_CHARGE_POINT_DETECTED, data)

    send_email_to_dgec(audit_sample)
    return SuccessResponse(data)


def send_email_to_dgec(audit_sample: ElecAuditSample):
    auditor = audit_sample.auditor.name
    cpo = audit_sample.cpo.name
    year = audit_sample.created_at.year

    admin_link = f"{CarbureEnv.get_base_url()}/org/9/elec-admin-audit/{year}"

    if audit_sample.charge_point_application is not None:
        application_id = audit_sample.charge_point_application.pk
        admin_link += f"/charge-points/audit_in_progress#application/{application_id}"
    elif audit_sample.meter_reading_application is not None:
        application_id = audit_sample.meter_reading_application.pk
        admin_link += f"/meter_readings/audit_in_progress#application/{application_id}"

    text_message = f"""
    Bonjour,

    l'auditeur {auditor} vient de déposer un résultat d'audit dans son espace CarbuRe pour l'aménageur {cpo}.
    Veuillez vous connecter et valider directement le résultat dans votre espace CarbuRe via <a href="{admin_link}">ce lien</a>.

    Merci beaucoup,

    Bien cordialement,
    L'équipe CarbuRe
    """

    send_mail(
        subject="[CarbuRe] Nouveau résultat d'audit élec disponible",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["carbure@beta.gouv.fr"],
        fail_silently=False,
    )
