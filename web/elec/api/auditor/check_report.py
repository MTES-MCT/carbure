from django import forms
from django.http import HttpRequest
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.repositories.elec_audit_repository import ElecAuditRepository
from elec.services.import_elec_audit_report_excel import import_elec_audit_report_excel


class CheckReportForm(forms.Form):
    file = forms.FileField()
    audit_sample_id = forms.IntegerField()


class CheckReportError:
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NO_CHARGE_POINT_DETECTED = "NO_CHARGE_POINT_DETECTED"


@require_POST
@check_user_rights(entity_type=[Entity.AUDITOR])
def check_report(request: HttpRequest):
    form = CheckReportForm(request.POST, request.FILES)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    audit_sample_id = form.cleaned_data["audit_sample_id"]
    excel_file = form.cleaned_data["file"]

    audit_sample = ElecAuditRepository.get_audited_sample_by_id(request.user, audit_sample_id)

    if not audit_sample:
        return ErrorResponse(404, CarbureError.NOT_FOUND)

    audited_charge_points = audit_sample.audited_charge_points.all().select_related("charge_point")
    charge_point_audits, errors = import_elec_audit_report_excel(excel_file, audited_charge_points)

    data = {}
    data["file_name"] = excel_file.name
    data["charge_point_count"] = len(charge_point_audits)
    data["errors"] = []
    data["error_count"] = 0
    data["comment_count"] = len([cp for cp in charge_point_audits if cp.get("comment")])

    if len(errors) > 0:
        data["errors"] = errors
        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, CheckReportError.VALIDATION_FAILED, data)

    if len(charge_point_audits) == 0:
        data["errors"] = [{"error": "NO_CHARGE_POINT_DETECTED"}]
        data["error_count"] = 1
        return ErrorResponse(400, CheckReportError.NO_CHARGE_POINT_DETECTED, data)

    return SuccessResponse(data)
