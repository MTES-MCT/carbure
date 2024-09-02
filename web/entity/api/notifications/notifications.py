from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.models import CarbureNotification
from core.serializers import CarbureNotificationSerializer


@check_user_rights()
def get_notifications(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])
    notifications = CarbureNotification.objects.filter(dest_id=entity_id).order_by("-datetime")[0:15]
    data = CarbureNotificationSerializer(notifications, many=True).data
    return JsonResponse({"status": "success", "data": data})
