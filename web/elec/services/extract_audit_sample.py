import random
from collections import defaultdict
from django.db.models import QuerySet
from elec.models import ElecChargePoint


def extract_audit_sample(charge_points: QuerySet[ElecChargePoint], percentage: float):
    charge_point_sample: list[ElecChargePoint] = []
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
