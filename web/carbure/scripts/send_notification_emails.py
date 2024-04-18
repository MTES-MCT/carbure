import os
from typing import cast
import django
import datetime
import argparse
from django.utils import timezone
from django.template import loader
from django.db.models import Count, Min, Max
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureNotification, Entity, UserRights

MAX_NOTIF_PER_HOUR = 20


def send_notification_emails(test: bool = False) -> None:

    entities = Entity.objects.annotate(num_notifs=Count("carburenotification")).order_by("-num_notifs")
    domain = os.environ["ALLOWED_HOSTS"]
    one_hour_ago = pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(hours=1))
    email_notif_sent = 0
    entity_oldest_notif = {}
    beginning_of_today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    connection = get_connection()

    try:
        connection.open()
    except Exception:
        print("Could not connect to email backend")
        return

    for entity in entities:

        all_notifs = CarbureNotification.objects.filter(
            dest=entity,
            send_by_email=True,
            email_sent=False,
            datetime__gte=beginning_of_today,
        ).aggregate(Count("id"), Min("datetime"), Max("datetime"))

        if all_notifs["id__count"] > 0:
            entity_oldest_notif[entity] = all_notifs["datetime__min"]
    for entity, oldest_notif_dt in sorted(entity_oldest_notif.items(), key=lambda x: cast(int, x[1])):
        if not entity.notifications_enabled:
            continue

        # wait at least one hour before sending an email, in case more events are coming
        if oldest_notif_dt > one_hour_ago:
            print("Ignoring notifications for %s - Too soon" % (entity.name))
            continue

        print("#### ENTITY %s ####" % (entity.name))

        notifs = CarbureNotification.objects.filter(
            dest=entity,
            send_by_email=True,
            email_sent=False,
            datetime__gte=beginning_of_today,
        )

        correction_requests = notifs.filter(type=CarbureNotification.CORRECTION_REQUEST)
        correction_done = notifs.filter(type=CarbureNotification.CORRECTION_DONE)
        lots_rejected = notifs.filter(type=CarbureNotification.LOTS_REJECTED)
        lots_received = notifs.filter(type=CarbureNotification.LOTS_RECEIVED)
        lots_recalled = notifs.filter(type=CarbureNotification.LOTS_RECALLED)
        certificate_rejected = notifs.filter(type=CarbureNotification.CERTIFICATE_REJECTED)
        meter_readings_app_started = notifs.filter(type=CarbureNotification.METER_READINGS_APP_STARTED).first()
        meter_readings_app_ending_soon = notifs.filter(type=CarbureNotification.METER_READINGS_APP_ENDING_SOON).first()

        email_context = {
            "entity": entity,
            "nb_notifications": notifs.count(),
            "domain": domain,
            "correction_requests": correction_requests,
            "correction_done": correction_done,
            "lots_rejected": lots_rejected,
            "lots_received": lots_received,
            "lots_recalled": lots_recalled,
            "certificate_rejected": certificate_rejected,
            "meter_readings_app_started": meter_readings_app_started,
            "meter_readings_app_ending_soon": meter_readings_app_ending_soon,
        }

        html_message = loader.render_to_string("emails/notifications.v3.html", email_context)
        text_message = loader.render_to_string("emails/notifications.v3.txt", email_context)

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
            if notifs.filter(notify_administrator=True).count() > 0:
                cc = ["carbure@beta.gouv.fr"]

        msg = EmailMultiAlternatives(
            connection=connection,
            subject=email_subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            cc=cc,
        )

        msg.attach_alternative(html_message, "text/html")
        if not test:
            notifs.update(email_sent=True)
            msg.send()
        else:
            print(text_message)
        email_notif_sent += 1

        print("###################")

        if email_notif_sent >= MAX_NOTIF_PER_HOUR:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send email notifications")
    parser.add_argument("--test", action="store_true", default=False, dest="test", help="Do not actually send emails")
    args = parser.parse_args()
    send_notification_emails(args.test)
