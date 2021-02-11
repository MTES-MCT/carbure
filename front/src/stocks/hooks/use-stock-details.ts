import { useEffect } from "react"
import { useParams } from "react-router-dom"

import { LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"

import useTransactionForm, {
  toTransactionFormState,
  toTransactionPostData,
} from "transactions/hooks/use-transaction-form"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"
import * as api from "transactions/api"
import { useNotificationContext } from "common/components/notifications"
import { getFieldErrors } from "transactions/hooks/use-transaction-details"
import { getStockStatus } from "../api"

export default function useStockDetails(
  entity: EntitySelection,
  refresh: () => void
) {
  const params: { id: string } = useParams()
  const notifications = useNotificationContext()

  const close = useClose("../")
  const [form, hasChange, change, setForm] = useTransactionForm(entity, true)
  const [details, resolveDetails] = useAPI(api.getDetails)
  const [request, resolveUpdate] = useAPI(api.updateLot)

  const entityID = entity?.id
  const txID = parseInt(params.id, 10)
  const tx = details.data?.transaction

  const fieldErrors = details.data ? getFieldErrors(details.data.errors) : {}
  const validationErrors = details.data?.errors.validation_errors ?? []
  const status = tx && entity ? getStockStatus(tx, entity) : LotStatus.Weird

  function refreshDetails() {
    if (typeof entityID !== "undefined") {
      resolveDetails(entityID, txID)
    }
  }

  async function submit() {
    if (!entityID) return

    const res = await resolveUpdate(entityID, txID, toTransactionPostData(form))

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

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveDetails(entityID, txID)
    }
  }, [resolveDetails, entityID, txID])

  useEffect(() => {
    if (tx) {
      setForm(toTransactionFormState(tx))
    }
  }, [tx, setForm])

  return {
    form,
    hasChange,
    details,
    fieldErrors,
    validationErrors,
    status,
    request,
    change,
    submit,
    close,
    refreshDetails,
  }
}
