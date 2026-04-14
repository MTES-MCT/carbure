from edelivery.tests.ebms.fixtures.udb_xml_data import transaction_data


def eo_get_transaction_response_payload(nb_transactions=1, **kwargs):
    transactions = "".join([transaction_data(**kwargs) for i in range(0, nb_transactions)])

    return f"""\
<udb:EOGetTransactionResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="e0907dde-11f5-423b-90e7-6a79728a5ef8"
            PROCESSING_DATE="2025-12-23T11:11:57.548+01:00"
            STATUS="FOUND" />
  <EO_TRANS_HEADER>
    {transactions}
  </EO_TRANS_HEADER>
</udb:EOGetTransactionResponse>"""
