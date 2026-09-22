from unittest import TestCase

from edelivery.ebms.request_responses.get_organisation_by_id_response import GetOrganisationByIDResponse
from edelivery.tests.ebms.fixtures.payloads import get_organisation_by_id_response_payload


class GetOrganisationByIDResponseTest(TestCase):
    def test_returns_found_organisations(self):
        payload = get_organisation_by_id_response_payload("FR_SIREN_CD000001111", "FR_SIREN_CD000009999", status="FOUND")
        response = GetOrganisationByIDResponse(payload)
        result = response.post_retrieval_action_result()

        expected_result = {"search_status": "FOUND", "found_organisations": ["FR_SIREN_CD000001111", "FR_SIREN_CD000009999"]}
        self.assertEqual(expected_result, result)

    def test_returns_correct_search_status(self):
        payload = get_organisation_by_id_response_payload("FR_SIREN_CD000001111", status="PARTIAL")
        response = GetOrganisationByIDResponse(payload)
        result = response.post_retrieval_action_result()
        self.assertEqual({"search_status": "PARTIAL", "found_organisations": ["FR_SIREN_CD000001111"]}, result)
