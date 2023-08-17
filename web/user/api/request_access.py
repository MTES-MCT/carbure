from core.decorators import otp_or_403
from core.models import Entity, UserRights
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse


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
        rr, created = UserRights.objects.update_or_create(
            user=request.user, entity=entity, defaults={"role": role, "status": UserRights.ACCEPTED}
        )
    else:
        UserRights.objects.update_or_create(
            user=request.user, entity=entity, defaults={"role": role, "status": UserRights.PENDING}
        )

        email_subject = "Carbure - Demande d'accès"
        message = """
        Bonjour,
        Un utilisateur vient de faire une demande d'accès à CarbuRe

        Utilisateur: %s
        Société: %s
        Commentaire: %s
        """ % (
            request.user.email,
            entity.name,
            comment,
        )

        send_mail(
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["carbure@beta.gouv.fr"],
            fail_silently=False,
        )
    return JsonResponse({"status": "success"})
