import io

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from biomethane.factories import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.services.supply_plan_excel_template import KEY_ROW, MAIN_SHEET_NAME
from core.models import Entity, MatierePremiere
from core.tests_utils import setup_current_user


class ExcelImportActionMixinTests(APITestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer Entity",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "password123",
            [(self.producer_entity, "RW")],
        )

        # Create MatierePremiere for testing
        MatierePremiere.objects.create(
            name="Lisiers bovins",
            name_en="Cattle slurry",
            code="LISIERS_BOVINS",
            is_methanogenic=True,
        )

        self.current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        self.url = reverse("biomethane-supply-plan-import-excel")

    def create_test_excel_file(self, data=None):
        """Create a test Excel file with supply plan structure"""
        if data is None:
            data = [{"year": 2024, "volume": 100}]

        df = pd.DataFrame(data)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            # Same sheet name and header row as template (keys on KEY_ROW)
            df.to_excel(writer, sheet_name=MAIN_SHEET_NAME, index=False, startrow=KEY_ROW)

        excel_buffer.seek(0)
        return SimpleUploadedFile(
            "test_supply_plan.xlsx",
            excel_buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_api_file_validation_integration(self):
        """Test API-level file validation"""
        # Test missing file
        response = self.client.post(
            self.url, {}, query_params={"entity_id": self.producer_entity.id, "year": self.current_year}, format="multipart"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("file", response.data)

        # Test invalid file type
        invalid_file = SimpleUploadedFile("test.txt", b"This is not an Excel file", content_type="text/plain")
        response = self.client.post(
            self.url,
            {"file": invalid_file},
            query_params={"entity_id": self.producer_entity.id, "year": self.current_year},
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)

    def test_import_excel_success(self):
        """Test successful import of valid Excel file"""
        excel_file = self.create_test_excel_file(
            data=[
                {
                    "feedstock": "Lisiers bovins",
                    "material_unit": "Brute",
                    "volume": 100,
                    "origin_department": "44 - Loire-Atlantique",
                    "average_weighted_distance_km": 50,
                    "maximum_distance_km": 100,
                    "origin_country": "France",
                },
                {
                    "feedstock": "Lisiers bovins",
                    "material_unit": "Sèche",
                    "dry_matter_ratio_percent": "13,00",
                    "volume": 100,
                    "origin_department": "",
                    "average_weighted_distance_km": 50,
                    "maximum_distance_km": 100,
                    "origin_country": "Allemagne",
                },
            ]
        )

        response = self.client.post(
            self.url,
            {"file": excel_file},
            query_params={"entity_id": self.producer_entity.id, "year": self.current_year},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("rows_imported", response.data)
        self.assertEqual(response.data["rows_imported"], 2)

    def test_export_excel_success(self):
        """Test successful export returns 200 and an xlsx file with Content-Disposition."""
        supply_plan = BiomethaneSupplyPlanFactory.create(producer=self.producer_entity, year=self.current_year)
        BiomethaneSupplyInputFactory.create(supply_plan=supply_plan)

        url = reverse("biomethane-supply-plan-export-excel")
        response = self.client.get(
            url,
            {"entity_id": self.producer_entity.id, "year": self.current_year},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Content-Disposition", response)
        self.assertTrue(
            response["Content-Disposition"].endswith('.xlsx"') or ".xlsx" in response["Content-Disposition"],
            msg="Content-Disposition should mention .xlsx file",
        )
        # xlsx files are ZIP-based: first bytes are PK
        self.assertTrue(
            response.content.startswith(b"PK"),
            msg="Response content should be a valid xlsx (ZIP signature)",
        )
