"""
Python vs SQL status must stay in sync for the current declaration year (dashboard scope).
"""

from datetime import date
from unittest.mock import patch

from django.db.models import OuterRef, Subquery
from django.test import TestCase

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity

DATE_PATCH = "biomethane.services.annual_declaration.date"


class DeclarationStatusAnnotationTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.producer = Entity.objects.create(
            name="Contract Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def assert_python_and_sql_status_match(self, declaration, expected):
        """Compare get_declaration_status and the SQL annotation for the same inputs."""
        python_status = BiomethaneAnnualDeclarationService.get_declaration_status(declaration)
        sql_status = self._status_from_sql(declaration)

        self.assertEqual(python_status, expected)
        self.assertEqual(sql_status, expected)

    def _status_from_sql(self, declaration):
        # Case when there is no declaration for producer
        if declaration is None:
            year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
            subquery = BiomethaneAnnualDeclaration.objects.filter(
                producer=OuterRef("pk"),
                year=year,
            )
            return (
                Entity.objects.filter(pk=self.producer.pk)
                .annotate(_status=Subquery(subquery.values("status")[:1]))
                .annotate(_computed=BiomethaneAnnualDeclarationService.get_declaration_status_annotation("_status"))
                .values_list("_computed", flat=True)
                .get()
            )

        current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        return (
            BiomethaneAnnualDeclaration.objects.filter(pk=declaration.pk, year=current_year)
            .annotate(_computed=BiomethaneAnnualDeclarationService.get_declaration_status_annotation("status"))
            .values_list("_computed", flat=True)
            .get()
        )

    @patch(DATE_PATCH)
    def test_not_started(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 30)

        self.assert_python_and_sql_status_match(None, BiomethaneAnnualDeclaration.NOT_STARTED)

    @patch(DATE_PATCH)
    def test_in_progress_before_deadline(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 30)
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer,
            year=2025,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        self.assert_python_and_sql_status_match(declaration, BiomethaneAnnualDeclaration.IN_PROGRESS)

    @patch(DATE_PATCH)
    def test_overdue_after_31st_march(self, mock_date):
        mock_date.today.return_value = date(2026, 4, 1)
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer,
            year=2025,
            status=BiomethaneAnnualDeclaration.IN_PROGRESS,
        )

        self.assert_python_and_sql_status_match(declaration, BiomethaneAnnualDeclaration.OVERDUE)

    @patch(DATE_PATCH)
    def test_declared_after_31st_march(self, mock_date):
        mock_date.today.return_value = date(2026, 4, 1)
        declaration = BiomethaneAnnualDeclaration.objects.create(
            producer=self.producer,
            year=2025,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )

        self.assert_python_and_sql_status_match(declaration, BiomethaneAnnualDeclaration.DECLARED)
