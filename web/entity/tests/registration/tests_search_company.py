# test with : python web/manage.py test entity.api.registration.tests_search_company.EntityRegistrationSearchCompanyTest --keepdb  # noqa: E501

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user


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

    def test_search_company(self):
        response = self.client.post(
            reverse("api-entity-registration-search-company"),
            {"registration_id": "542051180"},
        )
        assert response.status_code == 200
        data = response.json()
        company_preview = data["data"]["company_preview"]
        assert company_preview["legal_name"] == "TOTALENERGIES SE"

    def test_search_company_already_exists(self):
        siren = "542051180"
        Entity.objects.create(name="name", registration_id=siren)

        response = self.client.post(
            reverse("api-entity-registration-search-company"),
            {"registration_id": siren},
        )
        assert response.status_code == 200
        data = response.json()
        warning = data["data"]["warning"]
        assert warning["code"] == "REGISTRATION_ID_ALREADY_USED"

    def test_search_unexisting_company(self):
        response = self.client.post(
            reverse("api-entity-registration-search-company"),
            {"registration_id": "753991464"},
        )
        assert response.status_code == 400
        data = response.json()
        error_code = data["error"]
        assert error_code == "NO_COMPANY_FOUND"
