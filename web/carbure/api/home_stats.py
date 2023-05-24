import datetime
import traceback

from core.models import CarbureLot, Entity
from django.db.models.aggregates import Count, Sum
from django.http.response import JsonResponse


def get_home_stats(request):
    try:
        today = datetime.date.today()
        lots = CarbureLot.objects.filter(
            delivery_type__in=[CarbureLot.BLENDING, CarbureLot.DIRECT, CarbureLot.RFC], year=today.year
        ).select_related("biofuel")
        total_volume = lots.aggregate(Sum("volume"))["volume__sum"] or 0
        total_volume_etbe = lots.filter(biofuel__code="ETBE").aggregate(Sum("volume"))["volume__sum"] or 0
        entity_count = (
            Entity.objects.filter(entity_type__in=[Entity.PRODUCER, Entity.TRADER, Entity.OPERATOR])
            .values("entity_type")
            .annotate(count=Count("id"))
        )
        entities = {}
        for r in entity_count:
            entities[r["entity_type"]] = r["count"]
        total = round(total_volume) - round(total_volume_etbe) + round(total_volume_etbe * 27 * 0.37 / 21)
        return JsonResponse({"status": "success", "data": {"total_volume": total / 1000, "entities": entities}})
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Could not compute statistics"})
