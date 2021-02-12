import sys, os
import django
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from core.models import SustainabilityDeclaration, LotV2


def main():
    # 1) fetch all non-validated declarations
    period = datetime.date.today() - datetime.timedelta(days=30)
    period = period.replace(day=1)
    declarations = SustainabilityDeclaration.objects.filter(period=period, declared=False)

    for declaration in declarations:
        context = {}
        context['entity_id'] = declaration.entity.id
        context['lots_validated'] = LotV2.objects.filter(added_by=declaration.entity, status='Validated').count()
        period = declaration.period.strftime('%Y-%m')
        context['PERIOD'] = period
        email_subject = 'Carbure - Déclaration %s' % (period)
        html_message = render_to_string('emails/relance_mensuelle_fr.html', context)
        text_message = render_to_string('emails/relance_mensuelle_fr.txt', context)
        send_mail(
            subject=email_subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_message=html_message,
            recipient_list=['martin.planes@beta.gouv.fr'],
            fail_silently=False,
        )

if __name__ == '__main__':
    main()
