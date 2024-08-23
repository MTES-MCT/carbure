from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.models import CarbureNotification


@check_user_rights()
def ack_notifications(request, *args, **kwargs):
    entity_id = int(kwargs["context"]["entity_id"])
    notification_ids = request.POST.getlist("notification_ids", False)
    notifications = CarbureNotification.objects.filter(dest_id=entity_id, id__in=notification_ids)
    notifications.update(acked=True)
    return JsonResponse({"status": "success"})
