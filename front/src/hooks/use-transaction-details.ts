import { useEffect } from "react"
import { useParams } from "react-router-dom"

import { Errors, LotStatus } from "../services/types"
import { EntitySelection } from "./helpers/use-entity"

import useTransactionForm, { toTransactionFormState } from "./helpers/use-transaction-form" // prettier-ignore
import useAPI from "./helpers/use-api"
import useClose from "./helpers/use-close"
import * as api from "../services/lots"

function getFieldErrors(errors: Errors) {
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
  refresh: () => void
) {
  const params: { id: string } = useParams()

  const close = useClose("../")
  const [form, change, setForm] = useTransactionForm()
  const [details, resolveDetails] = useAPI(api.getDetails)
  const [request, resolve] = useAPI(api.updateLot)

  const txID = parseInt(params.id, 10)
  const tx = details.data?.transaction

  const fieldErrors = details.data ? getFieldErrors(details.data.errors) : {}
  const validationErrors = details.data?.errors.validation_errors ?? []
  const status = tx ? tx.status : LotStatus.Weird

  // if form data is not initialized, fill it instantly with data coming from transaction list
  if (tx && (form.id === -1 || form.id !== tx.id)) {
    // initialize the form with data coming from the loaded transaction
    setForm(toTransactionFormState(tx))
  }

  async function submit() {
    if (entity === null) return

    const res = await resolve(entity.id, txID, form)

    if (res) {
      refresh()
    }
  }

  useEffect(() => {
    if (entity) {
      return resolveDetails(entity.id, txID).cancel
    }
  }, [entity?.id, txID])

  return {
    form,
    details,
    fieldErrors,
    validationErrors,
    status,
    request,
    change,
    submit,
    close,
  }
}
