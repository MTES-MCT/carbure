import { useEffect } from "react"
import { useParams } from "react-router-dom"

import { Errors, LotStatus } from "../services/types"
import { EntitySelection } from "./helpers/use-entity"

import useTransactionForm, {
  toTransactionFormState,
  toTransactionPostData,
} from "./helpers/use-transaction-form"

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
  const [form, hasChange, change, setForm] = useTransactionForm(entity)
  const [details, resolveDetails] = useAPI(api.getDetails)
  const [request, resolveUpdate] = useAPI(api.updateLot)
  const [comment, resolveComment] = useAPI(api.commentLot)

  const entityID = entity?.id
  const txID = parseInt(params.id, 10)
  const tx = details.data?.transaction

  const fieldErrors = details.data ? getFieldErrors(details.data.errors) : {}
  const validationErrors = details.data?.errors.validation_errors ?? []
  const status = tx && entity ? api.getStatus(tx, entity.id) : LotStatus.Weird

  // if form data is not initialized, fill it instantly with data coming from transaction list
  if (tx && (form.id === -1 || form.id !== tx.id)) {
    // initialize the form with data coming from the loaded transaction
    setForm(toTransactionFormState(tx))
  }

  function refreshDetails() {
    if (entityID) {
      resolveDetails(entityID, txID)
    }
  }

  async function submit() {
    if (!entityID) return

    const res = await resolveUpdate(entityID, txID, toTransactionPostData(form))

    if (res) {
      refresh()
      refreshDetails()
      setForm(form)
    }
  }

  async function addComment(message: string) {
    if (entityID) {
      await resolveComment(entityID, txID, message, "both")
      await resolveDetails(entityID, txID)
    }
  }

  useEffect(() => {
    if (entityID) {
      return resolveDetails(entityID, txID).cancel
    }
  }, [resolveDetails, entityID, txID])

  return {
    form,
    hasChange,
    details,
    comment,
    fieldErrors,
    validationErrors,
    status,
    request,
    change,
    submit,
    close,
    addComment,
    refreshDetails,
  }
}
