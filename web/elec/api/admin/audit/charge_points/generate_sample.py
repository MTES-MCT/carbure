from django import forms
from django.db import transaction
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_audit_charge_point import ElecAuditChargePoint
from elec.models.elec_audit_sample import ElecAuditSample
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer
from elec.services.extract_audit_sample import extract_audit_sample


class GenerateSampleErrors:
    ALREADY_AUDITED = "ALREADY_AUDITED"


class GenerateSampleForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ChargePointRepository.get_annotated_applications())
    percentage = forms.IntegerField(required=False)


@require_POST
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
@transaction.atomic
def generate_sample(request):
    form = GenerateSampleForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    percentage = (form.cleaned_data["percentage"] or 10) / 100

    application_audits = ElecAuditSample.objects.filter(charge_point_application=application)

    # delete any pending audit sample for this application
    application_audits.filter(status=ElecAuditSample.IN_PROGRESS).delete()

    # send an error if the audit is already in progress or done
    if application_audits.filter(status=ElecAuditSample.AUDITED).count() > 0:
        return ErrorResponse(GenerateSampleErrors.ALREADY_AUDITED)

    charge_points = ChargePointRepository.get_annotated_application_charge_points(application.cpo, application)
    charge_point_sample = extract_audit_sample(charge_points, percentage)

    new_audit = ElecAuditSample.objects.create(
        charge_point_application=application,
        cpo=application.cpo,
        percentage=percentage * 100,
    )

    charge_point_audits = [
        ElecAuditChargePoint(audit_sample=new_audit, charge_point=charge_point) for charge_point in charge_point_sample
    ]
    ElecAuditChargePoint.objects.bulk_create(charge_point_audits)

    return SuccessResponse(
        {
            "application_id": application.id,
            "percentage": new_audit.percentage,
            "charge_points": ElecChargePointSampleSerializer(charge_point_sample, many=True).data,
        }
    )
