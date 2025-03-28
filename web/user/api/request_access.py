from django.conf import settings
from django.http import JsonResponse

from core.decorators import otp_or_403
from core.helpers import send_mail
from core.models import Entity, UserRights, UserRightsRequests
from core.utils import CarbureEnv


@otp_or_403
def request_entity_access(request):
    entity_id = request.POST.get("entity_id", False)
    comment = request.POST.get("comment", "")
    role = request.POST.get("role", False)

    if not entity_id:
        return JsonResponse({"status": "error", "message": "Missing entity_id"}, status=400)

    if not role:
        return JsonResponse({"status": "error", "message": "Please specify a role"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find entity"}, status=400)

    if request.user.is_staff:
        rr, created = UserRightsRequests.objects.update_or_create(
            user=request.user, entity=entity, defaults={"comment": comment, "role": role, "status": "ACCEPTED"}
        )
        UserRights.objects.update_or_create(
            user=rr.user, entity=entity, defaults={"role": rr.role, "expiration_date": rr.expiration_date}
        )
    else:
        UserRightsRequests.objects.update_or_create(
            user=request.user, entity=entity, defaults={"comment": comment, "role": role, "status": "PENDING"}
        )

        validation_url = f"{CarbureEnv.get_base_url()}/org/{entity_id}/settings#users"
        email_subject = "Carbure - Demande d'accès"
        message = """
        Bonjour,
        Un utilisateur vient de faire une demande d'accès à CarbuRe.
        Vous pouvez valider ou refuser cette demande depuis la page d'administration de votre société : %s.

        Utilisateur: %s
        Société: %s
        Commentaire: %s
        """ % (
            validation_url,
            request.user.email,
            entity.name,
            comment,
        )

        # get all user admins for tthe entity
        admins = UserRights.objects.filter(entity=entity, role=UserRights.ADMIN).values_list("user__email", flat=True)
        recipient_list = list(admins)
        recipient_list.append("carbure@beta.gouv.fr")

        send_mail(
            request=request,
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )
    return JsonResponse({"status": "success"})
