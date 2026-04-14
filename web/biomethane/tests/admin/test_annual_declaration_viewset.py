"""
Tests for BiomethaneAdminAnnualDeclarationViewSet.

Covers filtering of annual declarations by department (DREAL):
- by production unit (biomethane_production_unit__department) only
- ordering by priority (IN_PROGRESS first) then by producer name
- filters endpoint (department, status, tariff_reference)
"""

from datetime import date

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

    def setUp(self):
        self.user = setup_current_user(
            self,
            "dreal@example.com",
            "DREAL",
            "User",
            [(self.dreal, "ADMIN")],
        )

    def test_list_returns_only_declarations_from_accessible_departments(self):
        """list returns only declarations for producers whose unit is in an accessible department."""
        declaration_dept_01 = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        declaration_dept_02 = BiomethaneAnnualDeclaration.objects.create(
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
        data = response.json()
        results = data["results"]
        declaration_ids = [d["id"] for d in results]
        expected_declaration_ids = [declaration_dept_01.id, declaration_dept_02.id]

        self.assertEqual(declaration_ids, expected_declaration_ids)

    def test_list_includes_producers_without_unit_when_registered_zipcode_in_accessible_dept(self):
        """list includes producers without unit whose registered_zipcode is in the accessible departments list."""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_no_unit_zipcode_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(
            BiomethaneAnnualDeclaration.objects.get(pk=results[0]["id"]).producer_id,
            self.producer_no_unit_zipcode_01.id,
        )

    def test_list_excludes_producers_without_unit_when_registered_zipcode_not_in_accessible_dept(self):
        """list excludes producers without unit whose registered_zipcode is not in the accessible departments."""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_no_unit_zipcode_03,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data["results"]
        self.assertEqual(len(results), 0)

    def test_list_filters_by_current_year(self):
        """list returns only declarations for the current declaration year."""
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year - 1,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["year"], self.current_year)

    def test_list_is_ordered_by_priority_and_producer_name(self):
        """list returns declarations ordered by priority (IN_PROGRESS first) then by producer name."""
        EntityScope.objects.create(
            entity=self.dreal, content_type=ContentType.objects.get_for_model(Department), object_id=self.dept_03.id
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
        BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer_dept_01,
            year=self.current_year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data["results"]
        names = [d["producer"]["name"] for d in results]
        self.assertEqual(names, ["Producteur Dépt 02", "Producteur Dépt 03", "Producteur Dépt 01"])

    def test_list_different_dreal_sees_different_declarations(self):
        """A different DREAL only sees declarations for producers in its accessible departments."""
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
        data = response.json()
        results = data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(
            BiomethaneAnnualDeclaration.objects.get(pk=results[0]["id"]).producer_id,
            self.producer_dept_03.id,
        )

    def test_list_returns_empty_list_when_no_declarations(self):
        """list returns an empty list when no declarations match."""
        response = self.client.get(self.admin_declarations_url, {"entity_id": self.dreal.id})

        data = response.json()
        results = data["results"]

        self.assertEqual(len(results), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_applies_five_year_contract_filter_only_for_ademe(self):
        """ADEME only sees declarations where effective_date year is >= current year - 4."""
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
        declaration_eligible = BiomethaneAnnualDeclaration.objects.create(
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

        declaration_ids = [d["id"] for d in response.json()["results"]]

        self.assertEqual(declaration_ids, [declaration_eligible.id])

    def test_filters_return_expected_values_for_accessible_declarations(self):
        """filters endpoint returns only department, status and tariff_reference values from current year declarations in
        accessible departments."""
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
