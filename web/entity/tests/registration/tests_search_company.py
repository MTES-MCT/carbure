# test with : python web/manage.py test entity.api.registration.tests_search_company.EntityRegistrationSearchCompanyTest --keepdb  # noqa: E501

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user

MOCK_API_RESPONSE = {
    "results": [
        {
            "nom_complet": "TOTALENERGIES",
            "nom_raison_sociale": "TOTALENERGIES SE",
            "siren": "542051180",
            "siege": {
                "adresse": "2 PL JEAN MILLIER",
                "code_postal": "92400",
                "libelle_commune": "COURBEVOIE",
            },
        }
    ]
}


class EntityRegistrationSearchCompanyTest(TestCase):
    def setUp(self):
        self.cpo = Entity.objects.create(
            name="CPO",
            entity_type=Entity.CPO,
            has_elec=True,
        )
        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
        )
        self.api_patcher = patch("requests.get")
        self.mock_api = self.api_patcher.start()

    def tearDown(self):
        self.api_patcher.stop()

    def test_search_company(self):
        self.mock_api.return_value.json.return_value = MOCK_API_RESPONSE

        response = self.client.post(
            reverse("api-entity-registration-search-company"),
            {"registration_id": "542051180"},
        )

        self.mock_api.assert_called_once_with("https://recherche-entreprises.api.gouv.fr/search?q=542051180")

        assert response.status_code == 200
        data = response.json()
        company_preview = data["company_preview"]
        assert company_preview["legal_name"] == "TOTALENERGIES SE"
        assert company_preview["registered_city"] == "COURBEVOIE"
        assert company_preview["registered_zipcode"] == "92400"
        assert company_preview["registered_address"] == "2 PL JEAN MILLIER"

    def test_search_company_already_exists(self):
        self.mock_api.return_value.json.return_value = MOCK_API_RESPONSE

        siren = "542051180"
        Entity.objects.create(name="name", registration_id=siren)

        response = self.client.post(
            reverse("api-entity-registration-search-company"),
            {"registration_id": siren},
        )

        assert response.status_code == 200
        data = response.json()
        warning = data["warning"]
        assert warning["code"] == "REGISTRATION_ID_ALREADY_USED"

    def test_search_unexisting_company(self):
        self.mock_api.return_value.json.return_value = {"results": []}

        response = self.client.post(
            reverse("api-entity-registration-search-company"),
            {"registration_id": "753991464"},
        )

        assert response.status_code == 400
        data = response.json()
        error_code = data["error"]
        assert error_code == "NO_COMPANY_FOUND"

    def test_api_failure(self):
        self.mock_api.side_effect = Exception("API failure")

        response = self.client.post(
            reverse("entity-registration-search-company"),
            {"registration_id": "542051180"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "NO_COMPANY_FOUND"
