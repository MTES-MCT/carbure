import { useParams } from "react-router-dom"

import { Lots } from "../services/types"
import { EntitySelection } from "./helpers/use-entity"

import useTransactionForm, { toTransactionFormState } from "./helpers/use-transaction-form" // prettier-ignore
import useAPI, { ApiState } from "./helpers/use-api"
import useClose from "./helpers/use-close"
import { updateLot } from "../services/lots"

export default function useTransactionDetails(
  entity: EntitySelection,
  transactions: ApiState<Lots | null>,
  refresh: () => void
) {
  const close = useClose("../")
  const params: { id: string } = useParams()
  const [form, change, setForm] = useTransactionForm()
  const [request, resolve] = useAPI(updateLot)

  const transactionID = parseInt(params.id, 10)

  // if form data is not initialized, fill it instantly with data coming from transaction list
  if (transactions.data && (form.id === -1 || form.id !== transactionID)) {
    // find the relevant lot
    // @TODO would be nice to be able to fetch details for only one lot
    const transaction = transactions.data?.lots.find(
      (lot) => lot.id === transactionID
    )

    if (transaction) {
      // initialize the form with data coming from the loaded transaction
      setForm(toTransactionFormState(transaction))
    } else {
      // if transaction can't be loaded, close the modal
      // (in a setImmediate so it's executed outside the render loop)
      setImmediate(close)
    }
  }

  async function submit() {
    if (entity === null) return

    const res = await resolve(entity, transactionID, form)

    if (res) {
      refresh()
      close()
    }
  }

  return { form, request, change, submit, close }
}
