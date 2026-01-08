from collections import defaultdict

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ModelViewSet

from core.filters import FiltersActionFactory
from core.models import Entity, Pays
from elec.filters.provision_certificates import ProvisionCertificateFilter
from elec.models import ElecProvisionCertificate

DisableMigrations = defaultdict(lambda: None)


class ProvisionCertificateFiltersViewSet(FiltersActionFactory(), ModelViewSet):
    action_map = {}
    queryset = ElecProvisionCertificate.objects.all()
    filterset_class = ProvisionCertificateFilter


class FiltersActionFactoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country, _ = Pays.objects.get_or_create(
            code_pays="FR",
            defaults={
                "name": "France",
                "name_en": "France",
            },
        )
        cls.cpo = Entity.objects.create(
            name="Filter CPO 1",
            entity_type=Entity.CPO,
            has_elec=True,
        )
        cls.other_cpo = Entity.objects.create(
            name="Filter CPO 2",
            entity_type=Entity.CPO,
            has_elec=True,
        )

        ElecProvisionCertificate.objects.create(
            cpo=cls.cpo,
            quarter=1,
            year=2023,
            operating_unit="OU-1",
            source=ElecProvisionCertificate.MANUAL,
            energy_amount=100.0,
        )
        ElecProvisionCertificate.objects.create(
            cpo=cls.cpo,
            quarter=2,
            year=2023,
            operating_unit="OU-2",
            source=ElecProvisionCertificate.MANUAL,
            energy_amount=200.0,
        )
        ElecProvisionCertificate.objects.create(
            cpo=cls.other_cpo,
            quarter=3,
            year=2024,
            operating_unit="OU-3",
            source=ElecProvisionCertificate.METER_READINGS,
            energy_amount=300.0,
        )

    def setUp(self):
        self.factory = APIRequestFactory()

    def get_view(self, params=None):
        request = self.factory.get("/provision-certificates/filters", data=params or {})
        view = ProvisionCertificateFiltersViewSet()
        view.request = view.initialize_request(request)
        view.kwargs = {}
        view.args = ()
        view.action = "filters"
        return view

    def test_get_available_filters_excludes_method_filters(self):
        available_filters = self.get_view().get_available_filter_fields()

        # the FilterSet exposes ordering and model filters, but not ones using custom methods
        self.assertIn("year", available_filters)
        self.assertIn("operating_unit", available_filters)
        self.assertNotIn("status", available_filters)  # comes from filter_status method
        self.assertNotIn("entity_id", available_filters)  # explicitly excluded

    def test_filters_action_returns_distinct_values(self):
        view = self.get_view({"filter": "operating_unit", "cpo": self.cpo.name})

        response = view.filters(view.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, ["OU-1", "OU-2"])

    def test_filters_action_ignores_requested_filter_when_listing_options(self):
        view = self.get_view({"filter": "operating_unit", "operating_unit": "OU-1"})

        response = view.filters(view.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, ["OU-1", "OU-2", "OU-3"])

    def test_filters_action_rejects_unknown_filter(self):
        view = self.get_view({"filter": "unknown"})

        with self.assertRaises(Exception) as exc:
            view.filters(view.request)

        self.assertIn("Available filters", str(exc.exception))

    def test_filters_action_requires_filter_param(self):
        view = self.get_view()

        with self.assertRaises(Exception) as exc:
            view.filters(view.request)

        self.assertEqual(str(exc.exception), "No filter was specified")
