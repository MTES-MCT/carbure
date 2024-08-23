from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse

from core.decorators import check_admin_rights
from core.models import ExternalAdminRights, UserRights, UserRightsRequests
from core.utils import CarbureEnv


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE, ExternalAdminRights.ELEC])
def update_right_request(request):
    urr_id = request.POST.get("id", False)
    status = request.POST.get("status", False)
    if not urr_id:
        return JsonResponse({"status": "error", "message": "Please provide an id"}, status=400)
    if not status:
        return JsonResponse({"status": "error", "message": "Please provide a status"}, status=400)

    try:
        right_request = UserRightsRequests.objects.get(id=urr_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find request"}, status=400)

    right_request.status = status
    right_request.save()

    if status == "ACCEPTED":
        UserRights.objects.update_or_create(
            entity=right_request.entity,
            user=right_request.user,
            defaults={"role": right_request.role, "expiration_date": right_request.expiration_date},
        )
        # send_mail
        email_subject = "Carbure - Demande acceptée"
        message = """
        Bonjour,

        Votre demande d'accès à la Société %s vient d'être validée par l'administration.

        """ % (
            right_request.entity.name
        )
        recipient_list = [right_request.user.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
        send_mail(
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    else:
        UserRights.objects.filter(entity=right_request.entity, user=request.user).delete()
    return JsonResponse({"status": "success"})
