from .base_request import BaseRequest


class GetOrganisationByIDRequest(BaseRequest):
    def __init__(self, ntr_id):
        body = f"""\
<udb:GetOrganisationByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_ID_HEADER>
    <EO_ID>
      <ECONOMIC_OPERATOR_NUMBER>{ntr_id}</ECONOMIC_OPERATOR_NUMBER>
    </EO_ID>
  </EO_ID_HEADER>
</udb:GetOrganisationByIDRequest>"""

        super().__init__(body)
