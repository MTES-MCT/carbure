import { useParams } from "react-router-dom"

import { Lots, LotStatus } from "../services/types"
import { EntitySelection } from "./helpers/use-entity"

import useTransactionForm, { toTransactionFormState } from "./helpers/use-transaction-form" // prettier-ignore
import useAPI, { ApiState } from "./helpers/use-api"
import useClose from "./helpers/use-close"
import { updateLot } from "../services/lots"

function getFieldErrors(txs: Lots, id: number) {
  const errors = txs.errors[id] ?? {}
  const fieldErrors: { [k: string]: string } = {}

  errors.lots_errors?.forEach((err) => {
    fieldErrors[err.field] = err.error
  })

  errors.tx_errors?.forEach((err) => {
    fieldErrors[err.field] = err.error
  })

  return fieldErrors
}

export default function useTransactionDetails(
  entity: EntitySelection,
  transactions: ApiState<Lots | null>,
  refresh: () => void
) {
  const close = useClose("../")
  const params: { id: string } = useParams()
  const [form, change, setForm] = useTransactionForm()
  const [request, resolve] = useAPI(updateLot)

  const txs = transactions.data
  const txID = parseInt(params.id, 10)

  // find the relevant lot
  // @TODO would be nice to be able to fetch details for only one lot
  const transaction = txs?.lots.find((lot) => lot.id === txID)

  const fieldErrors = txs ? getFieldErrors(txs, txID) : {}
  const validationErrors = txs?.errors[txID]?.validation_errors ?? []
  const status = transaction ? transaction.status : LotStatus.Weird

  // if form data is not initialized, fill it instantly with data coming from transaction list
  if (transactions.data && (form.id === -1 || form.id !== txID)) {
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

    const res = await resolve(entity.id, txID, form)

    if (res) {
      refresh()
    }
  }

  return {
    form,
    fieldErrors,
    validationErrors,
    status,
    request,
    change,
    submit,
    close,
  }
}
