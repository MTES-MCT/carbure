import logging
import math
import random

from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights
from django.http import JsonResponse

# Get an instance of a logger
logger = logging.getLogger(__name__)


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE])
def add_entity(request):
    name = request.POST.get("name", False)
    entity_type = request.POST.get("category", False)

    if not name:
        return JsonResponse({"status": "error", "message": "Please provide a value in field name"}, status=400)
    if not entity_type:
        return JsonResponse({"status": "error", "message": "Please provide a value in field Category"}, status=400)

    if entity_type not in [c[0] for c in Entity.ENTITY_TYPES]:
        return JsonResponse({"status": "error", "message": "Unknown Category"}, status=400)

    try:
        obj, created = Entity.objects.update_or_create(name=name, entity_type=entity_type)
    except Exception:
        return JsonResponse(
            {"status": "error", "message": "Unknown error. Please contact an administrator"}, status=400
        )
    return JsonResponse({"status": "success", "data": "Entity created"})


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
