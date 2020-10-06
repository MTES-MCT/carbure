import { useEffect } from "react"
import { useParams } from "react-router-dom"

import { Lots } from "../services/types"
import { EntitySelection } from "./use-app"

import useTransactionForm, {
  toTransactionFormState,
} from "./helpers/use-transaction-form"
import useAPI from "./helpers/use-api"
import useClose from "./helpers/use-close"
import { updateLot } from "../services/lots"

export default function useTransactionDetails(
  entity: EntitySelection,
  transactions: Lots | null
) {
  const close = useClose("/transactions")
  const params: { id: string } = useParams()
  const [form, change, setForm] = useTransactionForm()
  const [request, resolve] = useAPI()

  const transactionID = parseInt(params.id, 10)

  useEffect(() => {
    if (transactions) {
      // find the relevant lot
      // @TODO would be nice to be able to fetch details for only one lot
      const transaction = transactions.lots.find(
        (lot) => lot.id === transactionID
      )

      // initialize the form with data coming from the loaded transaction
      if (transaction) {
        setForm(toTransactionFormState(transaction))
      }
    }
  }, [transactionID, transactions, setForm])

  function submit() {
    if (entity.selected && form) {
      resolve(updateLot(entity.selected.id, transactionID, form).then(close))
    }
  }

  return { form, request, change, submit, close }
}
