from edelivery.ebms.request_responses.get_organisation_by_id_response import GetOrganisationByIDResponse

from .base_request import BaseRequest


class GetOrganisationByIDRequest(BaseRequest):
    def __init__(self, *ntr_ids):
        def eo_number_element(ntr_id):
            return f"<ECONOMIC_OPERATOR_NUMBER>{ntr_id}</ECONOMIC_OPERATOR_NUMBER>"

        eo_number_elements = [eo_number_element(ntr_id) for ntr_id in ntr_ids]
        body = f"""\
<udb:GetOrganisationByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_ID_HEADER>
    <EO_ID>
      {"\n".join(eo_number_elements)}
    </EO_ID>
  </EO_ID_HEADER>
</udb:GetOrganisationByIDRequest>"""

        super().__init__(body, GetOrganisationByIDResponse)
