from django.core.management.base import BaseCommand

from user.services import UserAnonymizationService


class Command(BaseCommand):
    help = "Deactivates and anonymizes inactive users based on their last login date"

    def handle(self, *args, **options):
        self.stdout.write("Starting inactive user processing...")

        count_deactivated, count_anonymized = UserAnonymizationService.process_inactive_users()

        self.stdout.write(self.style.SUCCESS("Processing completed:"))
        self.stdout.write(self.style.SUCCESS(f"- {count_deactivated} users deactivated (inactive for 18+ months)"))
        self.stdout.write(self.style.SUCCESS(f"- {count_anonymized} users anonymized (inactive for 3+ years)"))
