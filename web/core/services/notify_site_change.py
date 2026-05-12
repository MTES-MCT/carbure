from django.conf import settings
from django.db.models import Q
from django.forms import Form

from core.helpers import send_mail
from core.models.entity import Entity
from core.models.lot import CarbureLot
from core.models.user import UserRights
from saf.models.saf_ticket import SafTicket
from transactions.models.site import Site


def notify_site_change(site: Site, form: Form):
    email_subject = "CarbuRe - Un site lié à votre activité a été modifié"

    changes = build_changes(form)
    changes_summary = "\n".join(f'- {field} : "{old}" → "{new}"' for field, (old, new) in changes.items())

    message = f"""
Bonjour,

Nous souhaitons vous informer que certaines données du site "{site.name}" ont été mises à jour.

Modifications apportées :
{changes_summary}

Bien cordialement,
L'équipe CarbuRe
    """

    lots = CarbureLot.objects.filter(Q(carbure_production_site_id=site.pk) | Q(carbure_delivery_site_id=site.pk))
    tickets = SafTicket.objects.filter(reception_airport_id=site.pk)

    site_entities = site.entitysite_set.values_list("entity_id", flat=True).distinct()
    lot_suppliers = lots.values_list("carbure_supplier_id", flat=True).distinct()
    lot_clients = lots.values_list("carbure_client_id", flat=True).distinct()
    ticket_suppliers = tickets.values_list("supplier_id", flat=True).distinct()
    ticket_clients = tickets.values_list("client_id", flat=True).distinct()

    entity_ids = {site.created_by_id, *site_entities, *lot_suppliers, *lot_clients, *ticket_suppliers, *ticket_clients}
    entity_ids.discard(None)

    recipients = set()
    for entity in Entity.objects.filter(id__in=entity_ids):
        recipients.update(
            entity.get_users_emails(
                role__in=[UserRights.ADMIN, UserRights.RW],
                user__is_staff=False,
                user__is_superuser=False,
            )
        )

    if recipients:
        send_mail(
            request=None,
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(recipients),
        )


def build_changes(form: Form) -> dict[str, tuple[str, str]]:
    changes = {}
    for field in form.changed_data:
        label = form[field].label
        old_value = form.initial.get(field)
        new_value = form.cleaned_data[field]
        changes[label] = (old_value, new_value)
    return changes
