import { useParams } from "react-router-dom"

import { Lots } from "../services/types"
import { FormFields } from "./helpers/use-form"

import useTransactionForm, {
  toTransactionFormState,
  TransactionFormState,
} from "./helpers/use-transaction-form"

type TransactionDetailsHook = [
  TransactionFormState | null,
  <T extends FormFields>(e: React.ChangeEvent<T>) => void
]

export default function useTransactionDetails(
  transactions: Lots | null
): TransactionDetailsHook {
  const params: { id: string } = useParams()
  const [form, onChange, setForm] = useTransactionForm()

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

  return [form, onChange]
}
