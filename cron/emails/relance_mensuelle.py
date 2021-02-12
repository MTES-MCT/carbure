import sys, os
import django
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from core.models import SustainabilityDeclaration, LotV2, UserRights

ENVIRONMENT = os.environ['IMAGE_TAG']


def main():
    # 1) fetch all non-validated declarations
    period = datetime.date.today() - datetime.timedelta(days=30)
    period = period.replace(day=1)
    declarations = SustainabilityDeclaration.objects.filter(period=period, declared=False)

    # 2) for all pending declarations
    for declaration in declarations:
        context = {}
        context['entity_id'] = declaration.entity.id
        # 3) get some data and render email template
        context['lots_validated'] = LotV2.objects.filter(added_by=declaration.entity, status='Validated').count()
        period = declaration.period.strftime('%Y-%m')
        context['PERIOD'] = period
        email_subject = 'Carbure - Déclaration %s' % (period)
        html_message = render_to_string('emails/relance_mensuelle_fr.html', context)
        text_message = render_to_string('emails/relance_mensuelle_fr.txt', context)

        rights = UserRights.objects.filter(entity=declaration.entity)
        print('Sending automatic reminder for %s - %s' % (declaration.entity.name, period))
        # only send when in prod
        if ENVIRONMENT == 'prod':
            print('PROD - sending to actual users')
            recipients = [r.user.email for r in rights]
            send_mail(
                subject=email_subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=html_message,
                recipient_list=recipients,
                fail_silently=False,
            )
        else:
            # otherwise, hardcore recipients to us
            print('DEV - sending only to us')
            recipients = ['carbure@beta.gouv.fr']
            send_mail(
                subject=email_subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=html_message,
                recipient_list=recipients,
                fail_silently=False,
            )
            # and limit to a single email
            break

if __name__ == '__main__':
    main()
