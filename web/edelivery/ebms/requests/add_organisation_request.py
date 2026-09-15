from .base_request import BaseRequest


class AddOrganisationRequest(BaseRequest):
    def __init__(self, carbure_entity):
        body = f"""\
<udb:AddOrganisationRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_DETAIL_HEADER>
    <EO_DETAIL>
      <ECONOMIC_OPERATOR_NUMBER>{carbure_entity.ntr_id()}</ECONOMIC_OPERATOR_NUMBER>
      <ORGANISATION_NAME>{carbure_entity.name}</ORGANISATION_NAME>
      <COUNTRY_CODE>{carbure_entity.registered_country.code_pays}</COUNTRY_CODE>
      <LEGAL_TYPE>LEGAL_ENTITY</LEGAL_TYPE>
    </EO_DETAIL>
  </EO_DETAIL_HEADER>
</udb:AddOrganisationRequest>"""
        super().__init__(body)
