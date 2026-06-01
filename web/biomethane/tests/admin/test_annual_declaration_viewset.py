"""
Tests for BiomethaneAdminAnnualDeclarationViewSet.

Covers filtering of annual declarations by department (DREAL):
- by production unit (biomethane_production_unit__department) only
- ordering by status priority (NOT_STARTED, OVERDUE, IN_PROGRESS, DECLARED) then by producer name
- filters endpoint (department, status, tariff_reference)
"""

from datetime import date
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories import BiomethaneContractFactory, BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.models.biomethane_contract import BiomethaneContract
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views.admin import BiomethaneAdminAnnualDeclarationViewSet
from core.models import Department, Entity, ExternalAdminRights
from core.tests_utils import FiltersActionTestMixin, setup_current_user
from entity.models import EntityScope


class BiomethaneAdminAnnualDeclarationViewSetTest(TestCase, FiltersActionTestMixin):
    """Tests for BiomethaneAdminAnnualDeclarationViewSet (DREAL list of annual declarations)."""

    dashboard_date_target = "biomethane.services.admin_dashboard.date"

    @classmethod
    def setUpTestData(cls):
        cls.current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()

        # Departments
        cls.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        cls.dept_02 = Department.objects.create(code_dept="02", name="Aisne")
        cls.dept_03 = Department.objects.create(code_dept="03", name="Allier")

        # DREAL with access to departments 01 and 02
        cls.dreal = Entity.objects.create(name="DREAL Test", entity_type=Entity.EXTERNAL_ADMIN)
        dept_ct = ContentType.objects.get_for_model(Department)
        EntityScope.objects.create(entity=cls.dreal, content_type=dept_ct, object_id=cls.dept_01.id)
        EntityScope.objects.create(entity=cls.dreal, content_type=dept_ct, object_id=cls.dept_02.id)
        ExternalAdminRights.objects.create(entity=cls.dreal, right=ExternalAdminRights.DREAL)

        # Other DREAL with access only to department 03
        cls.dreal_other = Entity.objects.create(name="DREAL Other", entity_type=Entity.EXTERNAL_ADMIN)
        EntityScope.objects.create(entity=cls.dreal_other, content_type=dept_ct, object_id=cls.dept_03.id)
        ExternalAdminRights.objects.create(entity=cls.dreal_other, right=ExternalAdminRights.DREAL)

        # ADEME with access to departments 01 and 02
        cls.ademe = Entity.objects.create(name="ADEME Test", entity_type=Entity.EXTERNAL_ADMIN)
        EntityScope.objects.create(entity=cls.ademe, content_type=dept_ct, object_id=cls.dept_01.id)
        EntityScope.objects.create(entity=cls.ademe, content_type=dept_ct, object_id=cls.dept_02.id)
        ExternalAdminRights.objects.create(entity=cls.ademe, right=ExternalAdminRights.ADEME)

        # Producers with production unit (department known)
        cls.producer_dept_01 = Entity.objects.create(
            name="Producteur Dépt 01",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        BiomethaneProductionUnitFactory.create(
            producer=cls.producer_dept_01,
            name="Unité 01",
            department=cls.dept_01,
        )

        cls.producer_dept_02 = Entity.objects.create(
            name="Producteur Dépt 02",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        BiomethaneProductionUnitFactory.create(
            producer=cls.producer_dept_02,
            name="Unité 02",
            department=cls.dept_02,
        )

        cls.producer_dept_03 = Entity.objects.create(
            name="Producteur Dépt 03",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )
        BiomethaneProductionUnitFactory.create(
            producer=cls.producer_dept_03,
            name="Unité 03",
            department=cls.dept_03,
        )

        # Producer without production unit, with registered_zipcode = accessible dept code (01)
        cls.producer_no_unit_zipcode_01 = Entity.objects.create(
            name="Producteur sans unité zip 01",
            entity_type=Entity.BIOMETHANE_PRODUCER,
            registered_zipcode="01",
        )

        # Producer without production unit, with registered_zipcode = non-accessible dept code (03)
        cls.producer_no_unit_zipcode_03 = Entity.objects.create(
            name="Producteur sans unité zip 03",
            entity_type=Entity.BIOMETHANE_PRODUCER,
            registered_zipcode="03",
        )

        cls.admin_declarations_url = reverse("biomethane-admin-annual-declarations-list")
        cls.dashboard_date_before_overdue = date(cls.current_year + 1, 2, 15)
        cls.dashboard_date_after_overdue = date(cls.current_year + 1, 4, 15)

    def setUp(self):
        self.user = setup_current_user(
            self,
            "dreal@example.com",
            "DREAL",
            "User",
            [(self.dreal, "ADMIN")],
        )
        self.dashboard_date_patcher = patch(self.dashboard_date_target)
        self.mock_dashboard_date = self.dashboard_date_patcher.start()
        self.mock_dashboard_date.today.return_value = self.dashboard_date_before_overdue

    def tearDown(self):
        self.dashboard_date_patcher.stop()

    def test_list_returns_only_declarations_from_accessible_departments(self):
        """list returns only producers whose unit is in an accessible department."""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_02,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_03,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        producer_ids = [d["producer"]["id"] for d in results]

        self.assertEqual(set(producer_ids), {self.producer_dept_01.id, self.producer_dept_02.id})
        self.assertNotIn(self.producer_no_unit_zipcode_01.id, producer_ids)
        self.assertNotIn(self.producer_no_unit_zipcode_03.id, producer_ids)
        for result in results:
            self.assertEqual(result["year"], self.current_year)

    def test_list_filters_by_current_year(self):
        """list returns only declarations for the current declaration year."""

        setup_current_user(
            self,
            "dreal-other@example.com",
            "DREAL with dept 03",
            "User",
            [(self.dreal_other, "ADMIN")],
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_03,
            year=self.current_year - 1,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_03,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal_other.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["year"], self.current_year)

    def test_list_is_ordered_by_priority_and_producer_name(self):
        """list returns producers ordered by status priority, then by producer name."""
        EntityScope.objects.create(
            entity=self.dreal, content_type=ContentType.objects.get_for_model(Department), object_id=self.dept_03.id
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_03,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        expected_before_overdue = [
            ("Producteur Dépt 02", BiomethaneAnnualDeclaration.NOT_STARTED),
            ("Producteur Dépt 03", BiomethaneAnnualDeclaration.IN_PROGRESS),
            ("Producteur Dépt 01", BiomethaneAnnualDeclaration.DECLARED),
        ]
        expected_after_overdue = [
            ("Producteur Dépt 02", BiomethaneAnnualDeclaration.NOT_STARTED),
            ("Producteur Dépt 03", BiomethaneAnnualDeclaration.OVERDUE),
            ("Producteur Dépt 01", BiomethaneAnnualDeclaration.DECLARED),
        ]

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [(result["producer"]["name"], result["status"]) for result in response.json()["results"]],
            expected_before_overdue,
        )

        with patch(self.dashboard_date_target) as mock_date:
            mock_date.today.return_value = self.dashboard_date_after_overdue
            response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                [(result["producer"]["name"], result["status"]) for result in response.json()["results"]],
                expected_after_overdue,
            )

    def test_list_different_dreal_sees_different_declarations(self):
        """A different DREAL only sees producers in its accessible departments."""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_03,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        setup_current_user(
            self,
            "dreal_other@example.com",
            "DREAL Other",
            "User",
            [(self.dreal_other, "ADMIN")],
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal_other.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        producer_ids = [result["producer"]["id"] for result in results]

        self.assertEqual(producer_ids, [self.producer_dept_03.id])

    def test_list_returns_not_started_when_no_declarations(self):
        """list returns accessible producers with NOT_STARTED when no declaration exists."""
        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]

        self.assertEqual(len(results), 2)
        self.assertEqual(
            {result["producer"]["id"] for result in results},
            {self.producer_dept_01.id, self.producer_dept_02.id},
        )
        self.assertTrue(all(result["status"] == BiomethaneAnnualDeclaration.NOT_STARTED for result in results))

    def test_list_applies_five_year_contract_filter_only_for_ademe(self):
        """ADEME only sees producers with contractswhere effective_date year is >= current year - 4."""
        ineligible_effective_date = date(self.current_year - 5, 1, 1)
        eligible_effective_date = date(self.current_year - 4, 1, 1)

        BiomethaneContractFactory.create(
            producer=self.producer_dept_01,
            effective_date=ineligible_effective_date,
            has_complementary_investment_aid=True,
            complementary_aid_organisms=[BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME],
        )
        BiomethaneContractFactory.create(
            producer=self.producer_dept_02,
            effective_date=eligible_effective_date,
            has_complementary_investment_aid=True,
            complementary_aid_organisms=[BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME],
        )

        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_02,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        setup_current_user(
            self,
            "ademe@example.com",
            "ADEME",
            "User",
            [(self.ademe, "ADMIN")],
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.ademe.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        producer_ids = [result["producer"]["id"] for result in results]

        self.assertEqual(producer_ids, [self.producer_dept_02.id])

    def test_filters_return_expected_values_for_accessible_declarations(self):
        """filters endpoint returns department, status and tariff_reference values from accessible producers."""
        BiomethaneContractFactory.create(
            producer=self.producer_dept_01,
            tariff_reference="2011",
        )
        BiomethaneContractFactory.create(
            producer=self.producer_dept_02,
            tariff_reference="2023",
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_02,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        self.assertFilters(
            BiomethaneAdminAnnualDeclarationViewSet,
            {
                "department": ["01", "02"],
                "status": ["DECLARED", "IN_PROGRESS"],
                "tariff_reference": ["2011", "2023"],
            },
            entity=self.dreal,
        )
