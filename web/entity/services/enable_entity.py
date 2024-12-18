from django.conf import settings

from core.helpers import send_mail
from core.models import UserRights, UserRightsRequests
from core.utils import CarbureEnv


def enable_entity(entity, http_request):
    # get entity admin
    right_requests = UserRightsRequests.objects.filter(
        entity=entity,
        role=UserRightsRequests.ADMIN,
        status__in=["PENDING", "ACCEPTED"],
    )

    # validate admin rights request
    right_requests.update(status="ACCEPTED")

    # create user rights
    UserRights.objects.bulk_create(
        [
            UserRights(
                entity=req.entity,
                user=req.user,
                role=req.role,
                expiration_date=req.expiration_date,
            )
            for req in right_requests
        ]
    )

    # enable entity
    entity.is_enabled = True
    entity.save()

    # send email to user
    subject = "Demande d'inscription de société validée"
    recipient_list = [req.user.email for req in right_requests] or ["carbure@beta.gouv.fr"]
    text_message = f"""
    Bonjour,

    Votre demande d'inscription pour la société {entity.name} a été validée par l'administration.
    Vous pouvez désormais accéder à la société dans votre espace en tant qu'administrateur : {CarbureEnv.get_base_url()}/account

    Pour plus d'information veuillez consulter notre guide d'utilisation : https://carbure-1.gitbook.io/faq/

    Bien cordialement,
    L'équipe CarbuRe
    """  # noqa: E501

    send_mail(
        request=http_request,
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
