import argparse
import datetime
import os

import django
import pytz
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Max, Min
from django.template import loader

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import EmailNotification, Entity, UserRights  # noqa: E402

MAX_NOTIF_PER_HOUR = 10


def main(args):
    entities = Entity.objects.annotate(num_notifs=Count("emailnotification")).order_by("-num_notifs")

    one_hour_ago = pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(hours=1))
    email_notif_sent = 0

    entity_oldest_notif = {}

    for entity in entities:
        notifs = EmailNotification.objects.filter(entity=entity).aggregate(Count("id"), Min("datetime"), Max("datetime"))
        if notifs["id__count"] > 0:
            entity_oldest_notif[entity] = notifs["datetime__min"]

    for entity, oldest_notif_dt in sorted(entity_oldest_notif.items(), key=lambda x: x[1]):
        if not entity.notifications_enabled:
            continue

        # wait at least one hour before sending an email, in case more events are coming
        if oldest_notif_dt > one_hour_ago:
            print("Ignoring notifications for %s - Too soon" % (entity.name))
            continue

        notifs = EmailNotification.objects.filter(entity=entity)

        email_context = {
            "entity": entity,
            "notif_txs": [n for n in notifs if n.linked_tx is not None],
            "notif_declarations": [n for n in notifs if n.linked_declaration is not None],
            "nb_notifications": len(notifs),
        }
        html_message = loader.render_to_string("emails/notifications.html", email_context)
        text_message = loader.render_to_string("emails/notifications.txt", email_context)

        email_subject = "Carbure - %s nouvelles notifications" % (len(notifs))
        cc = None
        if os.getenv("IMAGE_TAG", "dev") != "prod":
            # send only to staff / superuser
            recipients = [r.user.email for r in UserRights.objects.filter(entity=entity, user__is_staff=True)]
        else:
            # PROD
            recipients = [
                r.user.email
                for r in UserRights.objects.filter(entity=entity, user__is_staff=False, user__is_superuser=False).exclude(
                    role__in=[UserRights.AUDITOR, UserRights.RO]
                )
            ]
            if notifs.filter(send_copy_to_admin=True).count() > 0:
                cc = "carbure@beta.gouv.fr"

        msg = EmailMultiAlternatives(
            subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc
        )
        msg.attach_alternative(html_message, "text/html")
        if not args.test:
            msg.send()
        else:
            print(text_message)

        email_notif_sent += 1
        notifs.delete()
        if email_notif_sent >= MAX_NOTIF_PER_HOUR:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send email notifications")
    parser.add_argument("--test", action="store_true", default=False, dest="test", help="Do not actually send emails")
    args = parser.parse_args()

    main(args)
