from datetime import date
from django import forms
from django.views.decorators.http import require_GET
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from django.core.paginator import Paginator
from math import floor
from core.carburetypes import CarbureError

from elec.repositories.charge_point_repository import ChargePointRepository
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationSerializer
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplication

import elec.services.meter_readings_application_quarter as quarters


class ApplicationsFilterForm(forms.Form):
    year = forms.IntegerField(required=False)
    status = forms.CharField(required=False)


class ApplicationsSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_applications(request, entity):
    applications_filter_form = ApplicationsFilterForm(request.GET)
    applications_sort_form = ApplicationsSortForm(request.GET)

    if not applications_filter_form.is_valid() or not applications_sort_form.is_valid():
        return ErrorResponse(
            400,
            CarbureError.MALFORMED_PARAMS,
            {**applications_filter_form.errors, **applications_sort_form.errors},
        )

    from_idx = applications_sort_form.cleaned_data["from_idx"] or 0
    limit = applications_sort_form.cleaned_data["limit"] or 25

    current_date = date.today()
    year, quarter = quarters.get_application_quarter(current_date)
    deadline, urgency_status = quarters.get_application_deadline(current_date, year, quarter)

    current_application = MeterReadingRepository.get_cpo_application_for_quarter(entity, year, quarter)
    applications = MeterReadingRepository.get_annotated_applications_by_cpo(entity)
    applications = filter_meter_readings_applications(applications, **applications_filter_form.cleaned_data)

    prefetched_charge_points_for_meter_readings_count = ChargePointRepository.get_charge_points_for_meter_readings(
        entity
    ).count()

    if applications_sort_form.cleaned_data["from_idx"] is not None:
        paginator = Paginator(applications, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)
        object_list = page.object_list
    else:
        object_list = applications
    serialized_applications = ElecMeterReadingApplicationSerializer(object_list, many=True).data
    serialized_current_application = ElecMeterReadingApplicationSerializer(current_application).data if current_application else None  # fmt:skip

    return SuccessResponse(
        {
            "applications": serialized_applications,
            "current_application": serialized_current_application,
            "current_application_period": {
                "year": year,
                "quarter": quarter,
                "deadline": str(deadline),
                "urgency_status": urgency_status,
                "charge_point_count": prefetched_charge_points_for_meter_readings_count,
            },
        }
    )


def filter_meter_readings_applications(applications, **filters):
    if filters["year"]:
        applications = applications.filter(created_at__year=filters["year"])

    if filters["status"]:
        status_mapping = {
            "PENDING": [ElecMeterReadingApplication.PENDING],
            "AUDIT_IN_PROGRESS": [ElecMeterReadingApplication.AUDIT_IN_PROGRESS],
            "AUDIT_DONE": [ElecMeterReadingApplication.AUDIT_DONE],
            "HISTORY": [ElecMeterReadingApplication.REJECTED, ElecMeterReadingApplication.ACCEPTED],
        }
        applications = applications.filter(status__in=status_mapping[filters["status"]])
    return applications
