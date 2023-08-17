from core.decorators import check_admin_rights
from django.http import JsonResponse
from core.models import ExternalAdminRights, UserRights

from core.models import UserRights
from django.conf import settings
from django.core.mail import send_mail


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE])
def update_right_request(request):
    urr_id = request.POST.get("id", False)
    status = request.POST.get("status", False)
    if not urr_id:
        return JsonResponse({"status": "error", "message": "Please provide an id"}, status=400)
    if not status:
        return JsonResponse({"status": "error", "message": "Please provide a status"}, status=400)

    try:
        rights = UserRights.objects.get(id=urr_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find request"}, status=400)

    rights.status = status
    rights.save()

    if status == "ACCEPTED":
        # send_mail
        email_subject = "Carbure - Demande acceptée"
        message = """
        Bonjour,

        Votre demande d'accès à la Société %s vient d'être validée par l'administration.

        """ % (
            rights.entity.name
        )

        send_mail(
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[rights.user.email],
            fail_silently=False,
        )
    return JsonResponse({"status": "success"})
