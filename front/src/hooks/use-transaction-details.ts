import { useParams } from "react-router-dom"

import { Lots } from "../services/types"

import useTransactionForm, {
  toTransactionFormState,
} from "./helpers/use-transaction-form"
import useClose from "./helpers/use-close"

export default function useTransactionDetails(transactions: Lots | null) {
  const close = useClose("/transactions")
  const params: { id: string } = useParams()
  const { form, change, setForm } = useTransactionForm()

  if (transactions) {
    const transactionID = parseInt(params.id, 10)

    // find the relevant lot
    // @TODO would be nice to be able to fetch details for only one lot
    const transaction = transactions.lots.find(
      (lot) => lot.lot.id === transactionID
    )

    // initialize the form with data coming from the loaded transaction
    if (transaction && form === null) {
      setForm(toTransactionFormState(transaction))
    }
  }

  return { form, change, close }
}
