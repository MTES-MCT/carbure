from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin

from csp.decorators import csp_exempt
import folium
from api.v3.admin.views import couleur, grade
from core.decorators import is_admin
from api.v4.helpers import filter_lots
from admin.helpers import get_admin_lots_by_status
from core.models import Entity


@is_admin
@csp_exempt
@xframe_options_sameorigin
def map(request):
    status = request.GET.get("status", False)
    entity_id = request.GET.get("entity_id", False)
    entity = Entity.objects.get(id=entity_id)
    lots = get_admin_lots_by_status(entity, status)
    lots = filter_lots(lots, request.GET, entity)

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
        except:
            print("Missing start or end gps coordinates")
            print(
                "Start %s : %s"
                % (v["carbure_production_site__name"].encode("utf-8"), v["carbure_production_site__gps_coordinates"])
            )
            print(
                "End %s : %s"
                % (v["carbure_delivery_site__name"].encode("utf-8"), v["carbure_delivery_site__gps_coordinates"])
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

    html = (
        """
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
    """
        % m._repr_html_()
    )

    return HttpResponse(html)
