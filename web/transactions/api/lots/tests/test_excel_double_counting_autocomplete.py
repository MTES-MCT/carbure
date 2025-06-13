import datetime
import tempfile

import openpyxl
from django.test import TestCase

from certificates.models import DoubleCountingRegistration
from core.common import convert_template_row_to_formdata
from core.models import Entity, Pays
from transactions.sanity_checks.helpers import get_prefetched_data


class DoubleCountingAutocompleteTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/ml.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.trader = Entity.objects.filter(entity_type=Entity.TRADER).first()
        self.producer = Entity.objects.filter(name="Bioenergie du Sud-Ouest", entity_type=Entity.PRODUCER).first()
        self.country = Pays.objects.filter(code_pays="FR").first()

        self.dc_cert = DoubleCountingRegistration.objects.create(
            certificate_id="FR_12345_2025",
            production_site=self.producer.entitysite_set.first().site,
            valid_from=datetime.date(2025, 1, 1),
            valid_until=datetime.date(2026, 12, 31),
        )

    def create_test_excel(self, rows_data):
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = [
            "champ_libre",
            "producer",
            "production_site",
            "production_site_reference",
            "production_site_country",
            "production_site_commissioning_date",
            "double_counting_registration",
            "supplier",
            "supplier_certificate",
            "volume",
            "biocarburant_code",
            "matiere_premiere_code",
            "pays_origine_code",
            "eec",
            "el",
            "ep",
            "etd",
            "eu",
            "esca",
            "eccs",
            "eccr",
            "eee",
            "dae",
            "client",
            "delivery_date",
            "delivery_site",
            "delivery_site_country",
            "delivery_type",
        ]
        ws.append(headers)

        for row_data in rows_data:
            ws.append(row_data)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(temp_file.name)
        return temp_file.name

    def test_double_counting_autocomplete_for_trader(self):
        """Info should be auto-completed for the trader entity"""
        prefetched_data = get_prefetched_data(self.trader)

        test_rows = [
            [
                "",  # champ_libre
                "",  # producer (vide)
                "",  # production_site (vide)
                "",  # production_site_reference
                "",  # production_site_country
                "",  # production_site_commissioning_date
                "FR_12345_2025",  # double_counting_registration
                "",  # supplier
                "",  # supplier_certificate
                1000,  # volume
                "ETH",  # biocarburant_code
                "COLZA",  # matiere_premiere_code
                "FR",  # pays_origine_code
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,  # GES values
                "DAE123",  # dae
                "Client Test",  # client
                "2023-06-15",  # delivery_date
                "Depot Test",  # delivery_site
                "DE",  # delivery_site_country
                "UNKNOWN",  # delivery_type
            ]
        ]
        filepath = self.create_test_excel(test_rows)

        try:
            result = convert_template_row_to_formdata(self.trader, prefetched_data, filepath)
            assert len(result) == 1
            lot_data = result[0]
            assert lot_data["unknown_producer"] == self.producer.name
            assert lot_data["unknown_production_site"] == self.dc_cert.production_site.name
            assert lot_data["production_country_code"] == "FR"
            assert lot_data["production_site_commissioning_date"] == datetime.date(2019, 1, 1)

        finally:
            import os

            os.unlink(filepath)

    def test_double_counting_no_autocomplete_for_producer(self):
        """Info should not be auto-completed for the producer entity"""
        prefetched_data = get_prefetched_data(self.producer)
        test_rows = [
            [
                "",  # champ_libre
                "",  # producer (même nom que l'entité)
                "SEQUOIA",  # production_site
                "",  # production_site_reference
                "FR",  # production_site_country
                "2020-01-01",  # production_site_commissioning_date
                "FR_12345_2025",  # double_counting_registration
                "",  # supplier
                "",  # supplier_certificate
                1000,  # volume
                "ETH",  # biocarburant_code
                "COLZA",  # matiere_premiere_code
                "FR",  # pays_origine_code
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,  # GES values
                "DAE123",  # dae
                "Client Test",  # client
                "2023-06-15",  # delivery_date
                "Depot Test",  # delivery_site
                "FR",  # delivery_site_country
                "UNKNOWN",  # delivery_type
            ]
        ]

        filepath = self.create_test_excel(test_rows)
        try:
            result = convert_template_row_to_formdata(self.producer, prefetched_data, filepath)
            assert len(result) == 1
            lot_data = result[0]
            assert lot_data["carbure_production_site"] == "SEQUOIA"

        finally:
            import os

            os.unlink(filepath)

    def test_double_counting_unknown_certificate(self):
        """Info should not be auto-completed for an unknown DC certificate"""
        prefetched_data = get_prefetched_data(self.trader)
        test_rows = [
            [
                "",  # champ_libre
                "Unknown Producer",  # producer
                "Unknown Site",  # production_site
                "",  # production_site_reference
                "DE",  # production_site_country
                "2019-01-01",  # production_site_commissioning_date
                "FR_99999_2023",  # double_counting_registration (inexistant)
                "",  # supplier
                "",  # supplier_certificate
                1000,  # volume
                "ETH",  # biocarburant_code
                "COLZA",  # matiere_premiere_code
                "FR",  # pays_origine_code
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,  # GES values
                "DAE123",  # dae
                "Client Test",  # client
                "2023-06-15",  # delivery_date
                "Depot Test",  # delivery_site
                "FR",  # delivery_site_country
                "UNKNOWN",  # delivery_type
            ]
        ]

        filepath = self.create_test_excel(test_rows)
        try:
            result = convert_template_row_to_formdata(self.trader, prefetched_data, filepath)
            assert len(result) == 1
            lot_data = result[0]
            assert lot_data["unknown_producer"] == "Unknown Producer"
            assert lot_data["unknown_production_site"] == "Unknown Site"
            assert lot_data["production_country_code"] == "DE"
            assert lot_data["production_site_commissioning_date"] == "2019-01-01"

        finally:
            import os

            os.unlink(filepath)
