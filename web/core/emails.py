
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

from django.template import loader
from django.conf import settings
import os
from core.models import UserRightsRequests, Entity, UserRights

def send_reject_email(vendor, txs):
    email_subject = 'Carbure - Lots Refusés'

    recipients = UserRightsRequests.objects.filter(entity=vendor, status="ACCEPTED")
    if os.getenv('IMAGE_TAG', 'dev') == 'prod':
        recipients_emails = [r.user.email for r in recipients if not r.user.is_staff]
    else:
        # only staff in staging/dev/local
        recipients_emails = [r.user.email for r in recipients if r.user.is_staff]

    email_context = {
        'txs': txs,
    }
    html_message = loader.render_to_string('emails/rejected_lots.html', email_context)
    text_message = loader.render_to_string('emails/rejected_lots.txt', email_context)
    #send_mail(
    #    subject=email_subject,
    #    message=text_message,
    #    from_email=settings.DEFAULT_FROM_EMAIL,
    #    html_message=html_message,
    #    recipient_list=recipients_emails,
    #    fail_silently=False,
    #)


def send_accepted_lot_in_correction_email(tx, recipients, cc):
    email_subject = 'Carbure - Correction %s - %s - %.2f%%' % (tx.dae, tx.lot.biocarburant.name, tx.lot.ghg_reduction)

    if os.getenv('IMAGE_TAG', 'dev') != 'prod':
        recipients = [r.user.email for r in UserRights.objects.filter(entity=tx.carbure_vendor, user__is_staff=True)]
        cc = None

    email_context = {
        'tx': tx,
    }
    html_message = loader.render_to_string('emails/accepted_lot_in_correction.html', email_context)
    text_message = loader.render_to_string('emails/accepted_lot_in_correction.txt', email_context)
    msg = EmailMultiAlternatives(subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc)
    msg.attach_alternative(html_message, "text/html")
    msg.send()


def daily_email():
    pass