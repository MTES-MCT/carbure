import random
from collections import defaultdict
from django import forms
from django.db.models import QuerySet
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.excel import ExcelResponse
from core.models import ExternalAdminRights
from elec.models import ElecChargePoint
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point_application import ElecChargePointApplicationDetailsSerializer
from elec.services.export_charge_point_excel import export_charge_points_sample_to_excel, export_charge_points_to_excel


class ApplicationDetailsForm(forms.Form):
    application_id = forms.ModelChoiceField(queryset=ChargePointRepository.get_annotated_applications())
    percentage = forms.IntegerField(required=False)
    export = forms.BooleanField(required=False)
    sample = forms.BooleanField(required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_application_details(request):
    form = ApplicationDetailsForm(request.GET)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    application = form.cleaned_data["application_id"]
    percentage = (form.cleaned_data["percentage"] or 10) / 100
    export = form.cleaned_data["export"]
    want_sample = form.cleaned_data["sample"]

    if export:
        charge_points = ChargePointRepository.get_annotated_application_charge_points(application.cpo, application)

        if want_sample:
            charge_point_sample = extract_sample(charge_points, percentage)
            excel_file = export_charge_points_sample_to_excel(charge_point_sample, application.cpo)
        else:
            excel_file = export_charge_points_to_excel(charge_points, application.cpo)

        return ExcelResponse(excel_file)

    charge_point_application = ElecChargePointApplicationDetailsSerializer(application).data
    return SuccessResponse(charge_point_application)


def extract_sample(charge_points: QuerySet[ElecChargePoint], percentage: float):
    charge_point_sample = []
    charge_points = charge_points.exclude(latitude=None, longitude=None)

    total_power = 0
    stations = defaultdict(list)

    # group charge points by station
    for charge_point in charge_points:
        total_power += charge_point.nominal_power
        stations[charge_point.station_id].append(charge_point)

    stations_list = list[list[ElecChargePoint]](stations.values())

    # pick a random charge point
    ref = random.choice(charge_points)

    # measure the distance between each station and this charge point
    station_distances = [(station, distance(ref, station[0])) for station in stations_list]

    # sort stations by their distance to this charge point
    sorted_stations = sorted(station_distances, key=lambda x: x[1])

    # compute how much power is needed
    remaining_power = total_power * percentage

    # iterate over the stations and add charge points to the sample until the wanted power is reached
    for station_charge_points, _ in sorted_stations:
        for charge_point in station_charge_points:
            charge_point_sample.append(charge_point)
            remaining_power -= charge_point.nominal_power

            if remaining_power <= 0:
                return charge_point_sample

    # in case of error
    return []


# copypasta https://stackoverflow.com/a/72621718
def distance(a: ElecChargePoint, b: ElecChargePoint):
    import math

    # Convert all angles to radians
    lat1_r = math.radians(a.latitude or 0)
    lon1_r = math.radians(a.longitude or 0)
    lat2_r = math.radians(b.latitude or 0)
    lon2_r = math.radians(b.longitude or 0)

    # Calculate the distance
    dp = math.cos(lat1_r) * math.cos(lat2_r) * math.cos(lon1_r - lon2_r) + math.sin(lat1_r) * math.sin(lat2_r)
    angle = math.acos(dp)

    earth_radius = 6371.0008  # kilometers

    return earth_radius * angle
