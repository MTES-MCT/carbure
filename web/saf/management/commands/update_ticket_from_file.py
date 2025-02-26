import pandas as pd
from django.core.management.base import BaseCommand

from saf.models import SafTicket
from transactions.models import Site


class Command(BaseCommand):
    # command: python web/manage.py update_ticket_from_file web/complete.xlsx
    help = "Updates SAF tickets from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to Excel file")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        try:
            df = pd.read_excel(file_path)

            # Counters for reporting
            updated_count = 0
            error_count = 0
            carbure_id = "Carbure ID"
            reception_airport_icao = "reception_airport_icao"
            tiruert = "TIRUERT"
            for _, row in df.iterrows():
                try:
                    # Get ticket by carbure_id
                    ticket = SafTicket.objects.get(carbure_id=row[carbure_id])

                    # Update reception airport
                    if reception_airport_icao in row and pd.notna(row[reception_airport_icao]):
                        ticket.reception_airport = Site.objects.filter(icao_code=row[reception_airport_icao]).first()
                        if ticket.reception_airport:
                            ticket.reception_airport.save()
                        else:
                            self.stdout.write(self.style.WARNING(f"ICAO code not found: {row[reception_airport_icao]}"))

                    # Update consumption type based on TIRUERT column
                    if tiruert in row and pd.notna(row[tiruert]):
                        tiruert_value = str(row[tiruert]).upper()
                        if tiruert_value == "OUI":
                            ticket.consumption_type = SafTicket.MAC
                        elif tiruert_value == "NON":
                            ticket.consumption_type = SafTicket.MAC_DECLASSEMENT

                    ticket.save()
                    updated_count += 1

                except SafTicket.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Ticket not found for carbure_id: {row['carbure_id']}"))
                    error_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error updating ticket {row['carbure_id']}: {str(e)}"))
                    error_count += 1

            self.stdout.write(self.style.SUCCESS(f"Update complete. {updated_count} tickets updated. {error_count} errors."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file: {str(e)}"))
