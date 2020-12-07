import React from "react"
import { TransactionOutSummaryFormState } from "transactions/hooks/use-transaction-out-summary"
import { Box } from "common/components"

type StockSendComplexFormProps = {
  data: TransactionOutSummaryFormState
  loading: boolean
}

export const StockSendComplexForm = ({
  data,
  loading,
}: StockSendComplexFormProps) => {
  return (
    <Box row>
      {loading && <p>Chargement</p>}
      {loading || (
        <table>
          <thead>
            <tr>
              <th>Dépôt source</th>
              <th>Client</th>
              <th>Destination</th>
              <th>Biocarburant</th>
              <th>Volume</th>
              <th>Réduction de GES Min</th>
              <th>Réduction de GES Max</th>
              <th>Blacklist matière première</th>
            </tr>
          </thead>
          <tbody>
            {data ? (
              <>
                <tr>
                  <td>
                    <select name="depot">
                      <option value="depot1">Terminal 1</option>
                      <option value="depot2">Rotterdam</option>
                      <option value="depot3">FOS</option>
                    </select>
                  </td>
                  <td>
                    <select name="client">
                      <option value="depot1">Total</option>
                      <option value="depot2">BP</option>
                      <option value="depot3">Repsol</option>
                    </select>
                  </td>
                  <td>
                    <select name="client">
                      <option value="depot1">Madrid Norte</option>
                      <option value="depot2">Dover</option>
                      <option value="depot3">Marseille</option>
                    </select>
                  </td>
                  <td>
                    <select name="bc">
                      <option value="depot1">Ethanol</option>
                      <option value="depot2">EMHU</option>
                    </select>
                  </td>
                  <td>
                    <input type="text" placeholder="45000"></input>
                  </td>
                  <td>
                    <input type="text" placeholder="50%"></input>
                  </td>
                  <td>
                    <input type="text" placeholder="75%"></input>
                  </td>
                  <td>
                    <select name="bc">
                      <option value="depot1">Wheat</option>
                      <option value="depot2">Beetroot</option>
                      <option value="depot2">Soy</option>
                      <option value="depot2">Palm Oil</option>
                    </select>
                  </td>
                </tr>
                <tr>
                  <td>
                    <select name="depot">
                      <option value="depot1">Terminal 1</option>
                      <option value="depot2">Rotterdam</option>
                      <option value="depot3">FOS</option>
                    </select>
                  </td>
                  <td>
                    <select name="client">
                      <option value="depot1">Total</option>
                      <option value="depot2">BP</option>
                      <option value="depot3">Repsol</option>
                    </select>
                  </td>
                  <td>
                    <select name="client">
                      <option value="depot1">Madrid Norte</option>
                      <option value="depot2">Dover</option>
                      <option value="depot3">Marseille</option>
                    </select>
                  </td>
                  <td>
                    <select name="bc">
                      <option value="depot1">Ethanol</option>
                      <option value="depot2">EMHU</option>
                    </select>
                  </td>
                  <td>
                    <input type="text" placeholder="45000"></input>
                  </td>
                  <td>
                    <input type="text" placeholder="50%"></input>
                  </td>
                  <td>
                    <input type="text" placeholder="75%"></input>
                  </td>
                  <td>
                    <select name="bc">
                      <option value="depot1">Wheat</option>
                      <option value="depot2">Beetroot</option>
                      <option value="depot2">Soy</option>
                      <option value="depot2">Palm Oil</option>
                    </select>
                  </td>
                </tr>
                <tr>
                  <td>
                    <select name="depot">
                      <option value="depot1">Terminal 1</option>
                      <option value="depot2">Rotterdam</option>
                      <option value="depot3">FOS</option>
                    </select>
                  </td>
                  <td>
                    <select name="client">
                      <option value="depot1">Total</option>
                      <option value="depot2">BP</option>
                      <option value="depot3">Repsol</option>
                    </select>
                  </td>
                  <td>
                    <select name="client">
                      <option value="depot1">Madrid Norte</option>
                      <option value="depot2">Dover</option>
                      <option value="depot3">Marseille</option>
                    </select>
                  </td>
                  <td>
                    <select name="bc">
                      <option value="depot1">Ethanol</option>
                      <option value="depot2">EMHU</option>
                    </select>
                  </td>
                  <td>
                    <input type="text" placeholder="45000"></input>
                  </td>
                  <td>
                    <input type="text" placeholder="50%"></input>
                  </td>
                  <td>
                    <input type="text" placeholder="75%"></input>
                  </td>
                  <td>
                    <select name="bc">
                      <option value="depot1">Wheat</option>
                      <option value="depot2">Beetroot</option>
                      <option value="depot2">Soy</option>
                      <option value="depot2">Palm Oil</option>
                    </select>
                  </td>
                </tr>
              </>
            ) : (
              <p>Pas de stock disponible</p>
            )}
          </tbody>
        </table>
      )}
      <input type="button" value="Send batch" />
    </Box>
  )
}

export default StockSendComplexForm
