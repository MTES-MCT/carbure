from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey
from rest_framework_simplejwt.tokens import AccessToken

from biomethane.factories import BiomethaneContractFactory, BiomethaneEnergyFactory, BiomethaneProductionUnitFactory
from biomethane.factories.supply_plan import BiomethaneSupplyInputFactory, BiomethaneSupplyPlanFactory
from biomethane.models import BiomethaneAnnualDeclaration, BiomethaneFeedstockTariffCoefficient, BiomethaneSupplyInput
from core.models import Entity, MatierePremiere, UserRights
from core.tests_utils import setup_current_user, setup_current_user_with_jwt
from entity.factories import EntityFactory

provider_test_middleware = [
    middleware for middleware in settings.MIDDLEWARE if middleware != "django_otp.middleware.OTPMiddleware"
]
authentication_middleware_index = provider_test_middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware")
provider_test_middleware.insert(authentication_middleware_index + 1, "django_otp.middleware.OTPMiddleware")


class BiomethaneProviderDeclarationViewSetTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("biomethane-provider-declarations-list")
        self.year = 2024

        self.provider = EntityFactory.create(name="Provider A", entity_type=Entity.BIOMETHANE_PROVIDER)
        self.other_provider = EntityFactory.create(name="Provider B", entity_type=Entity.BIOMETHANE_PROVIDER)
        self.user = setup_current_user_with_jwt(
            self, "provider@carbure.local", "Provider", "gogogo", [(self.provider, "RO")]
        )

    def _create_producer(self, name, buyer, status_=BiomethaneAnnualDeclaration.DECLARED, year=None):
        producer = EntityFactory.create(name=name, entity_type=Entity.BIOMETHANE_PRODUCER)
        BiomethaneContractFactory.create(producer=producer, buyer=buyer)
        BiomethaneAnnualDeclaration.objects.create(producer=producer, year=year or self.year, status=status_)
        return producer

    def _get(self, **params):
        return self.client.get(self.url, {"entity_id": self.provider.id, "year": self.year, **params})

    def _authenticated_api_client(self, token=None):
        _, api_key = APIKey.objects.create_key(name="provider integration")
        client = APIClient()
        client.credentials(
            HTTP_X_API_KEY=api_key,
            HTTP_AUTHORIZATION=f"Bearer {token or AccessToken.for_user(self.user)}",
        )
        return client

    def test_returns_declarations_of_any_status_of_own_contracts(self):
        """Declarations of any status of producers under contract with the provider are returned, with their status."""
        own = self._create_producer("Own", self.provider)
        in_progress = self._create_producer("In progress", self.provider, status_=BiomethaneAnnualDeclaration.IN_PROGRESS)
        self._create_producer("Other", self.other_provider)

        response = self._get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # An unfinished declaration of a past year is exposed with the virtual OVERDUE status
        self.assertEqual(
            {item["producer"]["id"]: item["status"] for item in response.data["results"]},
            {own.id: "DECLARED", in_progress.id: "OVERDUE"},
        )

    def test_year_filter(self):
        """The year filter restricts results to the requested year."""
        self._create_producer("Y2024", self.provider, year=2024)
        producer_2023 = self._create_producer("Y2023", self.provider, year=2023)

        response = self._get(year=2023)

        self.assertEqual([item["producer"]["id"] for item in response.data["results"]], [producer_2023.id])

    def test_year_is_required(self):
        """The year query parameter is mandatory."""
        response = self.client.get(self.url, {"entity_id": self.provider.id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_exposes_declaration_and_tariff_coefficient_fields(self):
        """Each item exposes declaration details and tariff coefficient information."""
        producer = self._create_producer("Producer", self.provider)
        BiomethaneProductionUnitFactory.create(
            producer=producer,
            site_siret="12345678901234",
            insee_code="75056",
            address="1 rue de Paris",
            postal_code="75001",
            city="Paris",
        )

        item = self._get().data["results"][0]

        self.assertEqual(
            set(item.keys()),
            {
                "status",
                "producer",
                "production_unit",
                "tariff_reference",
                "tariff_coefficients",
                "tariff_tonnages",
                "electricity_consumption",
                "energy_efficiency_coefficient",
            },
        )
        self.assertEqual(item["status"], "DECLARED")
        self.assertEqual(item["producer"]["id"], producer.id)
        self.assertEqual(
            item["production_unit"],
            {
                "site_siret": "12345678901234",
                "insee_code": "75056",
                "address": "1 rue de Paris",
                "postal_code": "75001",
                "city": "Paris",
            },
        )

    def test_tariff_coefficient_summary_uses_only_declaration_year_and_producer(self):
        producer = self._create_producer("Producer", self.provider)
        contract = producer.biomethane_contract
        contract.tariff_reference = "2011"
        contract.save(update_fields=["tariff_reference"])
        p1 = MatierePremiere.objects.create(name="P1 input", code="PROVIDER-P1", is_methanogenic=True)
        p2 = MatierePremiere.objects.create(name="P2 input", code="PROVIDER-P2", is_methanogenic=True)
        unclassified = MatierePremiere.objects.create(name="Other input", code="PROVIDER-OTHER", is_methanogenic=True)
        Coeff = BiomethaneFeedstockTariffCoefficient
        Coeff.objects.create(feedstock=p1, regime=Coeff.AT_2011, coefficient=Coeff.P1)
        Coeff.objects.create(feedstock=p2, regime=Coeff.AT_2011, coefficient=Coeff.P2)
        plan = BiomethaneSupplyPlanFactory.create(producer=producer, year=self.year)
        BiomethaneSupplyInputFactory.create(
            supply_plan=plan,
            feedstock=p1,
            material_unit=BiomethaneSupplyInput.DRY,
            volume=100,
            dry_matter_ratio_percent=40,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=plan,
            feedstock=p2,
            material_unit=BiomethaneSupplyInput.WET,
            volume=50,
        )
        BiomethaneSupplyInputFactory.create(
            supply_plan=plan,
            feedstock=unclassified,
            material_unit=BiomethaneSupplyInput.WET,
            volume=200,
        )
        other_year = BiomethaneSupplyPlanFactory.create(producer=producer, year=self.year - 1)
        BiomethaneSupplyInputFactory.create(
            supply_plan=other_year,
            feedstock=p1,
            material_unit=BiomethaneSupplyInput.WET,
            volume=500,
        )
        other_producer = self._create_producer("Other provider producer", self.other_provider)
        other_plan = BiomethaneSupplyPlanFactory.create(producer=other_producer, year=self.year)
        BiomethaneSupplyInputFactory.create(
            supply_plan=other_plan,
            feedstock=p1,
            material_unit=BiomethaneSupplyInput.WET,
            volume=500,
        )

        item = self._get().data["results"][0]

        self.assertEqual(item["tariff_reference"], "2011")
        self.assertEqual(
            item["tariff_coefficients"],
            {"p1": 50.0, "p2": 10.0, "p3": 0.0, "p": 0.0, "pef": 0.0, "non_primed": 40.0},
        )
        self.assertEqual(
            item["tariff_tonnages"],
            {"total": 500.0, "p1": 250.0, "p2": 50.0, "p3": 0.0, "p": 0.0, "pef": 0.0, "non_primed": 200.0},
        )

    def test_tariff_coefficient_summary_is_null_without_referential(self):
        self._create_producer("Producer", self.provider)

        item = self._get().data["results"][0]

        self.assertIsNone(item["tariff_coefficients"])
        self.assertIsNone(item["tariff_tonnages"])

    def test_tonnages_are_rounded_without_rounding_percentage_input(self):
        """Tonnages are rounded for output, but percentages use the unrounded difference."""
        p1 = MatierePremiere.objects.create(name="P1 input", code="PROVIDER-ROUND-P1", is_methanogenic=True)
        other = MatierePremiere.objects.create(name="Other input", code="PROVIDER-ROUND-OTHER", is_methanogenic=True)
        Coeff = BiomethaneFeedstockTariffCoefficient
        Coeff.objects.create(feedstock=p1, regime=Coeff.AT_2011, coefficient=Coeff.P1)

        for name, primed, non_primed in (
            ("Decimal", 1000.12, 155.57),
            ("Small", 0.9951, 0.0049),
            ("Total", 0.1, 0.2),
        ):
            producer = self._create_producer(name, self.provider)
            contract = producer.biomethane_contract
            contract.tariff_reference = "2011"
            contract.save(update_fields=["tariff_reference"])
            plan = BiomethaneSupplyPlanFactory.create(producer=producer, year=self.year)
            for feedstock, volume in ((p1, primed), (other, non_primed)):
                BiomethaneSupplyInputFactory.create(
                    supply_plan=plan, feedstock=feedstock, material_unit=BiomethaneSupplyInput.WET, volume=volume
                )

        items = {item["producer"]["name"]: item for item in self._get().data["results"]}
        self.assertEqual(items["Decimal"]["tariff_tonnages"]["non_primed"], 155.57)
        self.assertEqual(items["Small"]["tariff_tonnages"]["non_primed"], 0.0)
        self.assertEqual(items["Small"]["tariff_tonnages"]["p1"], 1.0)
        self.assertEqual(items["Small"]["tariff_coefficients"]["non_primed"], 0.49)
        self.assertEqual(items["Small"]["tariff_coefficients"]["p1"], 99.51)
        self.assertEqual(items["Total"]["tariff_tonnages"]["total"], 0.3)

    def test_tariff_coefficient_summaries_are_independent_for_multiple_contracts(self):
        first = self._create_producer("First", self.provider)
        second = self._create_producer("Second", self.provider)
        first.biomethane_contract.tariff_reference = "2011"
        first.biomethane_contract.save(update_fields=["tariff_reference"])
        second.biomethane_contract.tariff_reference = "2023"
        second.biomethane_contract.save(update_fields=["tariff_reference"])
        feedstock = MatierePremiere.objects.create(name="Input", code="PROVIDER-CONDITIONAL", is_methanogenic=True)
        Coeff = BiomethaneFeedstockTariffCoefficient
        Coeff.objects.create(feedstock=feedstock, regime=Coeff.AT_2011, coefficient=Coeff.P1)
        Coeff.objects.create(feedstock=feedstock, regime=Coeff.AT_2020_PLUS, coefficient=Coeff.PEF)
        for producer in (first, second):
            plan = BiomethaneSupplyPlanFactory.create(producer=producer, year=self.year)
            BiomethaneSupplyInputFactory.create(
                supply_plan=plan,
                feedstock=feedstock,
                material_unit=BiomethaneSupplyInput.WET,
                volume=100,
            )

        items = {item["producer"]["id"]: item for item in self._get().data["results"]}

        self.assertEqual(items[first.id]["tariff_coefficients"]["p1"], 100.0)
        self.assertEqual(items[first.id]["tariff_tonnages"]["p1"], 100.0)
        self.assertEqual(items[second.id]["tariff_coefficients"]["pef"], 100.0)
        self.assertEqual(items[second.id]["tariff_tonnages"]["pef"], 100.0)
        self.assertEqual(items[second.id]["tariff_tonnages"]["p1"], 0.0)
        self.assertEqual(items[second.id]["tariff_coefficients"]["non_primed"], 0.0)
        self.assertEqual(items[second.id]["tariff_tonnages"]["non_primed"], 0.0)

    def test_tariff_coefficient_summary_is_zero_without_inputs(self):
        producer = self._create_producer("Producer", self.provider)
        feedstock = MatierePremiere.objects.create(name="Input", code="PROVIDER-EMPTY", is_methanogenic=True)
        Coeff = BiomethaneFeedstockTariffCoefficient
        Coeff.objects.create(feedstock=feedstock, regime=Coeff.AT_2011, coefficient=Coeff.P1)

        item = self._get().data["results"][0]

        self.assertEqual(item["tariff_reference"], producer.biomethane_contract.tariff_reference)
        self.assertEqual(
            item["tariff_coefficients"],
            {"p1": 0.0, "p2": 0.0, "p3": 0.0, "p": 0.0, "pef": 0.0, "non_primed": 0.0},
        )
        self.assertEqual(
            item["tariff_tonnages"],
            {"total": 0.0, "p1": 0.0, "p2": 0.0, "p3": 0.0, "p": 0.0, "pef": 0.0, "non_primed": 0.0},
        )

    def test_energy_values_follow_tariff_and_declaration_year(self):
        """Energy values use the declaration year and the formula for the producer's tariff."""
        for tariff in ("2011", "2020", "2021", "2023"):
            producer = self._create_producer(tariff, self.provider)
            contract = producer.biomethane_contract
            contract.tariff_reference = tariff
            contract.save(update_fields=["tariff_reference"])
            BiomethaneEnergyFactory.create(
                producer=producer,
                year=self.year,
                purification_electric_consumption_kwe=200,
                purified_biogas_quantity_nm3=100,
                total_unit_electric_consumption_kwe=300,
                injected_biomethane_gwh_pcs_per_year=100,
            )
            BiomethaneEnergyFactory.create(
                producer=producer,
                year=self.year - 1,
                purification_electric_consumption_kwe=500,
                total_unit_electric_consumption_kwe=500,
            )

        items = {item["producer"]["name"]: item for item in self._get().data["results"]}
        for tariff in ("2011", "2020", "2021"):
            self.assertEqual(items[tariff]["electricity_consumption"], 200)
            self.assertEqual(items[tariff]["energy_efficiency_coefficient"], 2)
        self.assertEqual(items["2023"]["electricity_consumption"], 300)
        self.assertAlmostEqual(items["2023"]["energy_efficiency_coefficient"], 0.000003)

    def test_energy_values_are_zero_when_missing_or_denominator_is_zero(self):
        """Missing energy, missing consumption and zero denominators are represented as zero."""
        missing = self._create_producer("Missing", self.provider)
        for tariff in ("2011", "2023"):
            producer = self._create_producer(tariff, self.provider)
            contract = producer.biomethane_contract
            contract.tariff_reference = tariff
            contract.save(update_fields=["tariff_reference"])
            BiomethaneEnergyFactory.create(
                producer=producer,
                year=self.year,
                purification_electric_consumption_kwe=None,
                purified_biogas_quantity_nm3=0,
                total_unit_electric_consumption_kwe=None,
                injected_biomethane_gwh_pcs_per_year=0,
            )
            zero_denominator = self._create_producer(f"{tariff} zero denominator", self.provider)
            contract = zero_denominator.biomethane_contract
            contract.tariff_reference = tariff
            contract.save(update_fields=["tariff_reference"])
            BiomethaneEnergyFactory.create(
                producer=zero_denominator,
                year=self.year,
                purification_electric_consumption_kwe=100,
                purified_biogas_quantity_nm3=0,
                total_unit_electric_consumption_kwe=100,
                injected_biomethane_gwh_pcs_per_year=0,
            )

        items = {item["producer"]["id"]: item for item in self._get().data["results"]}
        self.assertEqual(items[missing.id]["electricity_consumption"], 0)
        for item in items.values():
            expected_consumption = 100 if item["producer"]["name"].endswith("zero denominator") else 0
            self.assertEqual(item["electricity_consumption"], expected_consumption)
            self.assertEqual(item["energy_efficiency_coefficient"], 0)

    def test_production_unit_is_null_without_production_unit(self):
        """Without a production unit, production_unit is null."""
        self._create_producer("No unit", self.provider)

        item = self._get().data["results"][0]

        self.assertIsNone(item["production_unit"])

    def test_forbidden_for_another_provider_entity(self):
        """A provider cannot read through another provider entity it has no rights on."""
        response = self.client.get(self.url, {"entity_id": self.other_provider.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_for_non_provider_entity(self):
        """An entity that is not a biomethane provider cannot access the API."""
        producer = self._create_producer("Producer", self.provider)
        setup_current_user_with_jwt(self, "producer@carbure.local", "Producer", "gogogo", [(producer, "ADMIN")])

        response = self.client.get(self.url, {"entity_id": producer.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_without_entity_id(self):
        """Without entity_id, access is denied."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_without_api_key_nor_session(self):
        """Without an API key and without a frontend session, access is denied."""
        self.client.credentials()
        self.client.force_authenticate(user=None)

        response = self._get()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_with_invalid_api_key(self):
        """An invalid API key is rejected even for a user with rights on the provider entity."""
        self.client.credentials(HTTP_X_API_KEY="invalid")

        response = self._get()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accepts_a_real_signed_jwt(self):
        """A signed JWT and a valid API key authenticate the provider API request."""
        response = self._authenticated_api_client().get(self.url, {"entity_id": self.provider.id, "year": self.year})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rejects_an_invalid_jwt(self):
        """A valid API key does not compensate for an invalid JWT."""
        response = self._authenticated_api_client("not.a.valid.jwt").get(self.url, {"entity_id": self.provider.id})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_an_expired_jwt(self):
        """An expired but correctly signed JWT is rejected."""
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=timedelta(seconds=-1))

        response = self._authenticated_api_client(token).get(self.url, {"entity_id": self.provider.id})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_a_revoked_api_key(self):
        """A revoked API key is rejected even when the JWT is valid."""
        api_key, key = APIKey.objects.create_key(name="revoked provider key")
        api_key.revoked = True
        api_key.save(update_fields=["revoked"])
        client = APIClient()
        client.credentials(
            HTTP_X_API_KEY=key,
            HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.user)}",
        )

        response = client.get(self.url, {"entity_id": self.provider.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(MIDDLEWARE=provider_test_middleware)
class BiomethaneProviderDeclarationFrontTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("biomethane-provider-declarations-list")

        self.provider = EntityFactory.create(name="Provider A", entity_type=Entity.BIOMETHANE_PROVIDER)
        self.other_provider = EntityFactory.create(name="Provider B", entity_type=Entity.BIOMETHANE_PROVIDER)
        self.user = setup_current_user(self, "provider@carbure.local", "Provider", "gogogo", [(self.provider, "RO")])

    def _create_declaration(self, buyer, name="Producer"):
        producer = EntityFactory.create(name=name, entity_type=Entity.BIOMETHANE_PRODUCER)
        BiomethaneContractFactory.create(producer=producer, buyer=buyer)
        BiomethaneAnnualDeclaration.objects.create(producer=producer, year=2024, status=BiomethaneAnnualDeclaration.DECLARED)
        return producer

    def _verify_session_otp(self):
        device = EmailDevice.objects.create(user=self.user, name="email", confirmed=True)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    def test_session_user_without_api_key_can_list(self):
        """A frontend session user of the provider entity can list its declarations without API key."""
        producer = self._create_declaration(self.provider)
        self._create_declaration(self.other_provider, name="Other producer")
        self._verify_session_otp()

        response = self.client.get(self.url, {"entity_id": self.provider.id, "year": 2024})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["producer"]["id"] for item in response.data["results"]], [producer.id])

    def test_session_without_verified_otp_is_forbidden(self):
        """A logged-in session without a verified OTP cannot access the provider page API."""
        response = self.client.get(self.url, {"entity_id": self.provider.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revoked_provider_rights_block_the_next_session_request(self):
        """Removing provider rights immediately prevents further session access."""
        self._verify_session_otp()
        UserRights.objects.filter(user=self.user, entity=self.provider).delete()

        response = self.client.get(self.url, {"entity_id": self.provider.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_for_another_provider_entity(self):
        """A session user cannot read through another provider entity it has no rights on."""
        response = self.client.get(self.url, {"entity_id": self.other_provider.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_for_non_provider_entity(self):
        """A session user of a producer entity cannot access the provider declarations."""
        producer = self._create_declaration(self.provider)
        setup_current_user(self, "producer@carbure.local", "Producer", "gogogo", [(producer, "ADMIN")])

        response = self.client.get(self.url, {"entity_id": producer.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_when_not_authenticated(self):
        """An anonymous user cannot access the provider declarations."""
        self.client.logout()

        response = self.client.get(self.url, {"entity_id": self.provider.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
