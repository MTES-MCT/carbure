
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

from django.template import loader
from django.conf import settings
import os
from core.models import UserRightsRequests, Entity, UserRights



#def send_accepted_lot_in_correction_email(tx, recipients, cc):
#    email_subject = 'Carbure - Correction %s - %s - %.2f%%' % (tx.dae, tx.lot.biocarburant.name, tx.lot.ghg_reduction)##
#
#    if os.getenv('IMAGE_TAG', 'dev') != 'prod':
#        recipients = [r.user.email for r in UserRights.objects.filter(entity=tx.carbure_vendor, user__is_staff=True)]
#        cc = None
#
#    email_context = {
#        'tx': tx,
#    }
#    html_message = loader.render_to_string('emails/accepted_lot_in_correction.html', email_context)
#    text_message = loader.render_to_string('emails/accepted_lot_in_correction.txt', email_context)
#    msg = EmailMultiAlternatives(subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc)
#    msg.attach_alternative(html_message, "text/html")
#    msg.send()

