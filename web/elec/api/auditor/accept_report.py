from django import forms
from django.db import transaction
from django.http import HttpRequest
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models.elec_audit_charge_point import ElecAuditChargePoint
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
def accept_report(request: HttpRequest):
    form = AcceptReportForm(request.POST, request.FILES)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    audit_sample_id = form.cleaned_data["audit_sample_id"]
    excel_file = form.cleaned_data["file"]

    audit_sample = ElecAuditRepository.get_audited_sample_by_id(request.user, audit_sample_id)

    if not audit_sample:
        return ErrorResponse(404, CarbureError.NOT_FOUND)

    audited_charge_points = audit_sample.audited_charge_points.select_related("charge_point").all()
    charge_point_reports, errors = import_elec_audit_report_excel(excel_file)
    reports_by_charge_point_id = {report["charge_point_id"]: report for report in charge_point_reports}

    updated_audited_charge_point = []
    for charge_point_audit in audited_charge_points:
        charge_point_id = charge_point_audit.charge_point.charge_point_id
        report = reports_by_charge_point_id.get(charge_point_id, {})
        for key in report:
            setattr(charge_point_audit, key, report[key])
        updated_audited_charge_point.append(charge_point_audit)

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

    return SuccessResponse(data)
