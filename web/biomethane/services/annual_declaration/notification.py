import os

from django.conf import settings
from django.db import transaction

from biomethane.models import BiomethaneAnnualDeclaration
from core.helpers import send_mail
from core.models import UserRights

REOPEN_EMAIL_SUBJECT = "Carbure - Réouverture de votre déclaration {year}"
REOPEN_EMAIL_BODY = """Bonjour,
Nous vous informons que votre déclaration {year} dans CarbuRe a été réouverte.
Nous vous invitons à vous connecter via le lien ci-dessous afin de la finaliser.
{base_url}/org/{entity_id}/biomethane/{year}/supply-plan
L'équipe CarbuRe
"""


def get_reopen_notification_recipients(producer):
    return list(producer.get_users_emails(role__in=[UserRights.ADMIN, UserRights.RW]).order_by("user__email").distinct())


def notify_declaration_reopened(declaration, request=None):
    recipients = get_reopen_notification_recipients(declaration.producer)
    if not recipients:
        return recipients

    send_mail(
        request=request,
        subject=REOPEN_EMAIL_SUBJECT.format(year=declaration.year),
        message=REOPEN_EMAIL_BODY.format(
            year=declaration.year,
            entity_id=declaration.producer_id,
            base_url=os.environ.get("BASE_URL", "").rstrip("/"),
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
    )
    return recipients


def reopen_declaration(declaration, request=None):
    try:
        with transaction.atomic():
            declaration.is_open = True
            declaration.status = BiomethaneAnnualDeclaration.IN_PROGRESS
            declaration.save(update_fields=["is_open", "status"])
            return notify_declaration_reopened(declaration, request=request)
    except Exception:
        declaration.refresh_from_db(fields=["is_open", "status"])
        raise
