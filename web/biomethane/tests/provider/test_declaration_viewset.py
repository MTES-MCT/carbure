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

from biomethane.factories import BiomethaneContractFactory, BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneAnnualDeclaration
from core.models import Entity, UserRights
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
        return self.client.get(self.url, {"entity_id": self.provider.id, **params})

    def _authenticated_api_client(self, token=None):
        _, api_key = APIKey.objects.create_key(name="provider integration")
        client = APIClient()
        client.credentials(
            HTTP_X_API_KEY=api_key,
            HTTP_AUTHORIZATION=f"Bearer {token or AccessToken.for_user(self.user)}",
        )
        return client

    def test_returns_only_validated_declarations_of_own_contracts(self):
        """Only validated declarations of producers under contract with the provider are returned."""
        own = self._create_producer("Own", self.provider)
        self._create_producer("In progress", self.provider, status_=BiomethaneAnnualDeclaration.IN_PROGRESS)
        self._create_producer("Other", self.other_provider)

        response = self._get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["producer"]["id"] for item in response.data["results"]], [own.id])

    def test_year_filter(self):
        """The year filter restricts results to the requested year."""
        self._create_producer("Y2024", self.provider, year=2024)
        producer_2023 = self._create_producer("Y2023", self.provider, year=2023)

        response = self._get(year=2023)

        self.assertEqual([item["producer"]["id"] for item in response.data["results"]], [producer_2023.id])

    def test_response_exposes_producer_and_production_unit(self):
        """Each item exposes the producer and the location of its production unit."""
        producer = self._create_producer("Producer", self.provider)
        BiomethaneProductionUnitFactory.create(
            producer=producer, insee_code="75056", address="1 rue de Paris", postal_code="75001", city="Paris"
        )

        item = self._get().data["results"][0]

        self.assertEqual(set(item.keys()), {"producer", "production_unit"})
        self.assertEqual(item["producer"]["id"], producer.id)
        self.assertEqual(
            item["production_unit"],
            {"insee_code": "75056", "address": "1 rue de Paris", "postal_code": "75001", "city": "Paris"},
        )

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
        response = self._authenticated_api_client().get(self.url, {"entity_id": self.provider.id})

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

        response = self.client.get(self.url, {"entity_id": self.provider.id})

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
