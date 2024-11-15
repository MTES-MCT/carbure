import math
import random

import folium
from csp.decorators import csp_exempt
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.decorators import action


class MapMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        examples=[
            OpenApiExample(
                "Example of export response.",
                value="file.html",
                request_only=False,
                response_only=True,
                media_type="text/html",
            ),
        ],
        responses={
            (200, "text/html"): OpenApiTypes.STR,
        },
    )
    @csp_exempt
    @xframe_options_sameorigin
    @action(methods=["get"], detail=False)
    def map(self, request, *args, **kwargs):
        lots = self.filter_queryset(self.get_queryset())

        # on veut: nom site de depart, gps depart, nom site arrivee, gps arrivee, volume
        lots = lots.filter(carbure_production_site__isnull=False, carbure_delivery_site__isnull=False)
        values = lots.values(
            "carbure_production_site__name",
            "carbure_production_site__gps_coordinates",
            "carbure_delivery_site__name",
            "carbure_delivery_site__gps_coordinates",
        ).annotate(volume=Sum("volume"))

        volume_min = 999999
        volume_max = 0
        for v in values:
            volume = v["volume"]
            if volume < volume_min:
                volume_min = volume
            if volume > volume_max:
                volume_max = volume

        m = folium.Map(location=[46.227638, 2.213749], zoom_start=5)
        known_prod_sites = []
        known_depots = []
        for v in values:
            try:
                # start coordinates
                slat, slon = v["carbure_production_site__gps_coordinates"].split(",")
                # end coordinates
                elat, elon = v["carbure_delivery_site__gps_coordinates"].split(",")
            except Exception:
                print("Missing start or end gps coordinates")
                print(
                    "Start %s : %s"
                    % (
                        v["carbure_production_site__name"].encode("utf-8"),
                        v["carbure_production_site__gps_coordinates"],
                    )
                )
                print(
                    "End %s : %s"
                    % (
                        v["carbure_delivery_site__name"].encode("utf-8"),
                        v["carbure_delivery_site__gps_coordinates"],
                    )
                )
                continue

            if v["carbure_production_site__gps_coordinates"] not in known_prod_sites:
                known_prod_sites.append(v["carbure_production_site__gps_coordinates"])
                c = couleur()
                folium.Circle(
                    radius=50e2,
                    location=[slat, slon],
                    popup=v["carbure_production_site__name"],
                    color=c,
                    fill=True,
                    fill_opacity=1,
                ).add_to(m)
            if v["carbure_delivery_site__gps_coordinates"] not in known_depots:
                known_depots.append(v["carbure_delivery_site__gps_coordinates"])
                folium.Circle(
                    radius=50e2,
                    location=[elat, elon],
                    popup=v["carbure_delivery_site__name"],
                    color="white",
                    fill=True,
                    fill_opacity=1,
                ).add_to(m)
            volume = v["volume"]
            folium.PolyLine(
                [(float(slat), float(slon)), (float(elat), float(elon))],
                color=c,
                weight=grade(volume, volume_min, volume_max),
                line_cap="round",
                opacity=0.7,
                popup=v["carbure_production_site__name"]
                + " vers "
                + v["carbure_delivery_site__name"]
                + " : \n"
                + str(volume)
                + " litres",
            ).add_to(m)

        print(m._repr_html_()[0:50])
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Map</title>
</head>
<body style="margin: 0; overflow: hidden;">
%s
</body>
</html>
        """ % m._repr_html_()

        return HttpResponse(html)


# not an api endpoint
def couleur():
    liste = [
        "#FF0040",
        "#DF01A5",
        "#BF00FF",
        "#4000FF",
        "#0040FF",
        "#00BFFF",
        "#00FFBF",
        "#00FF40",
        "#40FF00",
        "#BFFF00",
        "#FFBF00",
        "#FF4000",
        "#FA5858",
        "#FAAC58",
        "#F4FA58",
        "#ACFA58",
        "#58FA58",
        "#58FAAC",
        "#58FAF4",
        "#58ACFA",
        "#5858FA",
        "#AC58FA",
        "#FA58F4",
        "#FA58AC",
        "#B40404",
        "#B45F04",
        "#AEB404",
        "#5FB404",
        "#04B45F",
        "#04B4AE",
        "#045FB4",
        "#0404B4",
        "#5F04B4",
        "#B404AE",
        "#B4045F",
        "#8A0829",
    ]
    return random.choice(liste)


# not an api endpoint


def grade(volume, min, max):
    # print(volume, min, max)
    weight = math.log(volume) / 5
    # print(weight)
    # 2 < x < 4
    # min < volume < max
    return weight
