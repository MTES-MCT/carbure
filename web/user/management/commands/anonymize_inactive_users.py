from django.conf import settings
from django.core.management.base import BaseCommand

from core.helpers import send_mail
from user.services import UserAnonymizationService


class Command(BaseCommand):
    help = "Deactivates and anonymizes inactive users based on their last login date"

    def handle(self, *args, **options):
        self.stdout.write("Starting inactive user processing...")

        count_deactivated, count_anonymized = UserAnonymizationService.process_inactive_users()

        self.stdout.write(self.style.SUCCESS("Processing completed:"))
        self.stdout.write(self.style.SUCCESS(f"- {count_deactivated} users deactivated (inactive for 18+ months)"))
        self.stdout.write(self.style.SUCCESS(f"- {count_anonymized} users anonymized (inactive for 3+ years)"))

        self.send_email_summary(count_deactivated, count_anonymized)

    def send_email_summary(self, count_deactivated, count_anonymized):
        # Send email to carbure
        subject = "Anonymisation / Désactivation des utilisateurs inactifs"
        recipient_list = ["carbure@beta.gouv.fr"]
        text_message = f"""
        Bonjour,

        {count_deactivated} utilisateur{' a été désactivé' if count_deactivated == 1 else 's ont été désactivés'} (inactifs depuis plus de 18 mois')
        {count_anonymized} utilisateur{' a été anonymisé' if count_anonymized == 1 else 's ont été anonymisés'} (inactifs depuis plus de 3 ans')

        Excellente journée à tous !
        """  # noqa: E501

        send_mail(
            request=None,
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )
