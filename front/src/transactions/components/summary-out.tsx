import React from "react"
// import { TransactionOutSummaryFormState } from "../hooks/use-transaction-out-summary"
import { Box } from "common/components"
import { TransactionOutSummaryFormState } from "stocks/components/send-complex-form"

type TransactionOutSummaryProps = {
  data: TransactionOutSummaryFormState
  loading: boolean
}

const TransactionOutSummaryTable = ({
  data,
  loading,
}: TransactionOutSummaryProps) => {
  return (
    <Box row>
      {loading && <p>Chargement</p>}
      {loading || (
        <table>
          <thead>
            <tr>
              <th>Client</th>
              <th>Site de Livraison</th>
              <th>Biocarburant</th>
              <th>Volume</th>
              <th>Réduction de GES</th>
            </tr>
          </thead>
          <tbody>
            {data ? (
              Object.entries(data).map(([client, delivery_sites]) =>
                Object.entries(delivery_sites).map(([delivery_site, biocarburants]) =>
                  Object.entries(biocarburants).map(
                    ([biocarburant, values]) => (
                      <tr>
                        <td>{client}</td>
                        <td>{delivery_site}</td>
                        <td>{biocarburant}</td>
                        <td>{values.volume}L</td>
                        <td>{values.avg_ghg_reduction}%</td>
                      </tr>
                    )
                  )
                )
              )
            ) : (
              <p>Aucun Lot sortant</p>
            )}
          </tbody>
        </table>
      )}
    </Box>
  )
}

export default TransactionOutSummaryTable
