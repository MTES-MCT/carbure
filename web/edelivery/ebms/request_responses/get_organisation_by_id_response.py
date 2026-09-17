from .base_request_response import BaseRequestResponse


class GetOrganisationByIDResponse(BaseRequestResponse):
    def post_retrieval_action_result(self):
        status = self.parsed_XML.find("./RESPONSE_HEADER").attrib["STATUS"]
        organisation_elements = self.parsed_XML.findall(".//ECONOMIC_OPERATOR_NUMBER")
        organisations = [oe.text for oe in organisation_elements]

        return {"search_status": status, "found_organisations": organisations}
