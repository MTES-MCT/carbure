
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
import os
from core.models import UserRightsRequests, Entity

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
  send_mail(
      subject=email_subject,
      message=text_message,
      from_email=settings.DEFAULT_FROM_EMAIL,
      html_message=html_message,
      recipient_list=recipients_emails,
      fail_silently=False,
  )

  # transactions forwarded and rejected disappear from the UI. Delete them
  for tx in txs:
    if tx.parent_tx is not None and tx.carbure_client.entity_type == Entity.OPERATOR:
      tx.delete()


def daily_email():
  pass