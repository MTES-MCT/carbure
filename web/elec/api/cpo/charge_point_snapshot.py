# /api/elec/provision-certificate/snapshot

import traceback

from django import forms
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from elec.api.cpo.charge_points.applications import filter_charge_point_applications
from elec.api.cpo.charge_points.charge_points import filter_charge_points
from elec.api.cpo.meter_readings.applications import filter_meter_readings_applications
from elec.models import ElecChargePoint, ElecChargePointApplication, ElecMeterReadingApplication


class ElecSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


class ElecSnapshotForm(forms.Form):
    entity_id = forms.IntegerField()
    category = forms.CharField()
    year = forms.IntegerField(required=False)
    application_date = forms.DateField(required=False)
    charge_point_id = forms.CharField(required=False)
    station_id = forms.CharField(required=False)
    latest_meter_reading_month = forms.IntegerField(required=False)
    is_article_2 = forms.BooleanField(required=False)
    search = forms.CharField(required=False)


@require_GET
@check_user_rights()
def get_charge_point_snapshot(request, *args, **kwargs):
    snapshot_form = ElecSnapshotForm(request.GET)

    if not snapshot_form.is_valid():
        return ErrorResponse(400, ElecSnapshotError.MALFORMED_PARAMS, snapshot_form.errors)

    entity_id = snapshot_form.cleaned_data["entity_id"]

    category = snapshot_form.cleaned_data["category"]

    if category == "charge_point_application":
        model_class = ElecChargePointApplication
        filter_method = filter_charge_point_applications
    elif category == "meter_reading_application":
        model_class = ElecMeterReadingApplication
        filter_method = filter_meter_readings_applications
    elif category == "charge_point":
        model_class = ElecChargePoint
        filter_method = filter_charge_points
    else:
        return ErrorResponse(400, ElecSnapshotError.MALFORMED_PARAMS, "Wrong category")

    charge_point_applications_count = ElecChargePointApplication.objects.filter(cpo_id=entity_id).count()
    meter_reading_applications_count = ElecMeterReadingApplication.objects.filter(cpo_id=entity_id).count()
    charge_points_count = ElecChargePoint.objects.filter(cpo_id=entity_id, is_deleted=False).count()
    try:
        items = model_class.objects.filter(cpo_id=entity_id, is_deleted=False)

        return SuccessResponse(
            {
                "charge_point_applications": charge_point_applications_count,
                "meter_reading_applications": meter_reading_applications_count,
                "charge_points": charge_points_count,
                "pending": filter_method(items, status="PENDING", **snapshot_form.cleaned_data).count(),
                "audit_in_progress": filter_method(items, status="AUDIT_IN_PROGRESS", **snapshot_form.cleaned_data).count(),
                "accepted": filter_method(items, status="ACCEPTED", **snapshot_form.cleaned_data).count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecSnapshotError.SNAPSHOT_FAILED)
