import { useEffect } from "react"
import { useParams } from "react-router-dom"

import { EntityType, Errors, LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"

import useTransactionForm, {
  toTransactionFormState,
  toTransactionPostData,
} from "transactions/hooks/use-transaction-form"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"
import { useNotificationContext } from "common/components/notifications"
import * as api from "../api"
import { getStatus } from "transactions/helpers"

export function getFieldErrors(errors: Errors) {
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
  const detailsGetter =
    entity?.entity_type === EntityType.Administration
      ? api.getAdminDetails
      : api.getDetails

  const params: { id: string } = useParams()
  const notifications = useNotificationContext()
  const close = useClose("../")

  const { data, hasChange, onChange, reset } = useTransactionForm(entity)

  const [details, resolveDetails] = useAPI(detailsGetter)
  const [request, resolveUpdate] = useAPI(api.updateLot)
  const [comment, resolveComment] = useAPI(api.commentLot)

  const entityID = entity?.id
  const txID = parseInt(params.id, 10)
  const tx = details.data?.transaction

  const fieldErrors = details.data ? getFieldErrors(details.data.errors) : {}
  const validationErrors = details.data?.errors.validation_errors ?? []
  const status = tx && entity ? getStatus(tx, entity.id) : LotStatus.Weird

  function refreshDetails() {
    if (typeof entityID !== "undefined") {
      resolveDetails(entityID, txID)
    }
  }

  async function submit() {
    if (typeof entityID === "undefined") return

    const res = await resolveUpdate(entityID, txID, toTransactionPostData(data))

    if (res) {
      refresh()
      refreshDetails()

      notifications.push({
        level: "success",
        text: "Le lot a bien été sauvegardé !",
      })
    } else {
      notifications.push({
        level: "error",
        text: "Impossible de sauvegarder ce lot.",
      })
    }
  }

  async function addComment(message: string) {
    if (typeof entityID !== "undefined") {
      await resolveComment(entityID, txID, message, "both")
      await resolveDetails(entityID, txID)
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveDetails(entityID, txID)
    }
  }, [resolveDetails, entityID, txID])

  useEffect(() => {
    if (tx) {
      reset(toTransactionFormState(tx))
    }
  }, [tx, reset])

  return {
    form: data,
    hasChange,
    details,
    comment,
    fieldErrors,
    validationErrors,
    status,
    request,
    change: onChange,
    submit,
    close,
    addComment,
    refreshDetails,
  }
}
