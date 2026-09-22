from edelivery.tests.ebms.fixtures.transaction_xml_data import transaction_xml_data


def eo_get_transaction_response_payload(nb_transactions=1, **kwargs):
    transactions = "".join([transaction_xml_data(**kwargs) for i in range(0, nb_transactions)])

    return f"""\
<udb:EOGetTransactionResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="e0907dde-11f5-423b-90e7-6a79728a5ef8"
            PROCESSING_DATE="2025-12-23T11:11:57.548+01:00"
            STATUS="FOUND" />
  <EO_TRANS_HEADER>
    {transactions}
  </EO_TRANS_HEADER>
</udb:EOGetTransactionResponse>"""


def get_organisation_by_id_response_payload(*ntr_ids, status):
    def eo_detail_element(ntr_id):
        return f"""\
<EO_DETAIL>
  <ECONOMIC_OPERATOR_NUMBER>{ntr_id}</ECONOMIC_OPERATOR_NUMBER>
  <!-- … -->
</EO_DETAIL>"""

    eo_detail_elements = [eo_detail_element(ntr_id) for ntr_id in ntr_ids]
    return f"""\
<udb:GetOrganisationByIDResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="5ab49022-da26-4b0c-8740-1a51952e83f7"
                   PROCESSING_DATE="2026-09-16T19:29:01.222+02:00" STATUS="{status}" />
  <EO_DETAIL_HEADER>
    {"\n".join(eo_detail_elements)}
  </EO_DETAIL_HEADER>
</udb:GetOrganisationByIDResponse>"""
