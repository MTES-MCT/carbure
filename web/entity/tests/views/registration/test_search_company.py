from unittest import TestCase
from unittest.mock import MagicMock, patch

from entity.views.registration.search_company import (
    CompanyNotFoundError,
    fetch_company_preview,
    get_department_from_postal_code,
)


def _make_api_response(results):
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": results}
    mock_response.raise_for_status.return_value = None
    return mock_response


def _make_etablissement(**overrides):
    defaults = {
        "code_postal": "75001",
        "libelle_commune": "PARIS",
        "commune": "75101",
        "departement": "75",
        "adresse": "1 RUE DE RIVOLI 75001 PARIS",
    }
    return {**defaults, **overrides}


def _make_company(*, siege=None, matching_etablissements=None):
    company = {
        "nom_complet": "Acme Corp",
        "nom_raison_sociale": "ACME",
        "siren": "123456789",
    }
    if siege is not None:
        company["siege"] = siege
    if matching_etablissements is not None:
        company["matching_etablissements"] = matching_etablissements
    return company


class GetDepartmentFromPostalCodeTest(TestCase):
    def test_metropolitan(self):
        self.assertEqual(get_department_from_postal_code("75001"), "75")
        self.assertEqual(get_department_from_postal_code("33000"), "33")

    def test_corsica(self):
        self.assertEqual(get_department_from_postal_code("20000"), "2A")
        self.assertEqual(get_department_from_postal_code("20200"), "2B")

    def test_dom_tom(self):
        self.assertEqual(get_department_from_postal_code("97100"), "971")
        self.assertEqual(get_department_from_postal_code("97600"), "976")


@patch("entity.views.registration.search_company.requests.get")
class FetchCompanyPreviewTest(TestCase):
    def test_siren_returns_preview_from_siege(self, mock_get):
        siege = _make_etablissement()
        company = _make_company(siege=siege)
        mock_get.return_value = _make_api_response([company])

        preview = fetch_company_preview("123456789")

        self.assertEqual(preview["name"], "Acme Corp")
        self.assertEqual(preview["registered_city"], "PARIS")
        self.assertEqual(preview["department_code"], "75")
        self.assertEqual(preview["registered_address"], "1 RUE DE RIVOLI")

    def test_siret_returns_preview_from_matching_etablissement(self, mock_get):
        etab = _make_etablissement(
            code_postal="69001", libelle_commune="LYON", commune="69381", adresse="5 PLACE BELLECOUR 69001 LYON"
        )
        company = _make_company(matching_etablissements=[etab], siege=_make_etablissement())
        mock_get.return_value = _make_api_response([company])

        preview = fetch_company_preview("12345678900001")

        self.assertEqual(preview["registered_city"], "LYON")
        self.assertEqual(preview["department_code"], "69")
        self.assertEqual(preview["registered_address"], "5 PLACE BELLECOUR")

    def test_empty_results_raises(self, mock_get):
        mock_get.return_value = _make_api_response([])

        with self.assertRaises(CompanyNotFoundError):
            fetch_company_preview("000000000")

    def test_siret_no_matching_etablissement_raises(self, mock_get):
        company = _make_company(matching_etablissements=[], siege=_make_etablissement())
        mock_get.return_value = _make_api_response([company])

        with self.assertRaises(CompanyNotFoundError):
            fetch_company_preview("00000000000000")

    def test_http_error_propagates(self, mock_get):
        from requests.exceptions import HTTPError

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("500")
        mock_get.return_value = mock_response

        with self.assertRaises(HTTPError):
            fetch_company_preview("123456789")
