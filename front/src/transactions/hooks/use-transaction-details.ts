import { useEffect } from "react"
import { useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"

import { EntityType, GenericError, LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"

import useTransactionForm, {
  toTransactionFormState,
  toTransactionPostData,
} from "transactions/hooks/use-transaction-form"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"
import { useNotificationContext } from "common/components/notifications"
import * as api from "../api"
import { getStatus } from "transactions/components/status"

export function useFieldErrors(errors: GenericError[]) {
  const { t } = useTranslation()
  const fieldErrors: { [k: string]: string } = {}

  errors.forEach((err) => {
    if (!err.is_blocking) return

    if (err.field) {
      fieldErrors[err.field] = t(err.error, { ns: "errors" })
    }

    if (err.fields) {
      err.fields?.forEach(
        (field) => (fieldErrors[field] = t(err.error, { ns: "errors" }))
      )
    }
  })

  return fieldErrors
}

function detailsGetter(entity: EntitySelection) {
  switch (entity?.entity_type) {
    case EntityType.Administration:
      return api.getAdminDetails
    case EntityType.Auditor:
      return api.getAuditorDetails
    default:
      return api.getDetails
  }
}

function notePoster(entity: EntitySelection) {
  switch (entity?.entity_type) {
    case EntityType.Administration:
      return api.addAdminComment
    case EntityType.Auditor:
      return api.addAuditorComment
    default:
      return async () => { }
  }
}

export default function useTransactionDetails(
  entity: EntitySelection,
  refresh: () => void
) {
  const { t } = useTranslation()
  const params = useParams<"id">()
  const notifications = useNotificationContext()
  const close = useClose("../")

  const { data, hasChange, onChange, reset } = useTransactionForm(entity)

  const [details, resolveDetails] = useAPI(detailsGetter(entity))
  const [request, resolveUpdate] = useAPI(api.updateLot)
  const [comment, resolveComment] = useAPI(api.commentLot)
  const [, resolveControlComment] = useAPI(notePoster(entity))

  const fieldErrors = useFieldErrors(details.data?.errors ?? [])

  const entityID = entity?.id
  const txID = parseInt(params.id ?? '', 10)
  const tx = details.data?.transaction

  const validationErrors = details.data?.errors ?? []
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
        text: t("Le lot a bien été sauvegardé !", { ns: "translation" }),
      })
    } else {
      notifications.push({
        level: "error",
        text: t("Impossible de sauvegarder ce lot.", { ns: "translation" }),
      })
    }
  }

  async function addComment(message: string) {
    if (typeof entityID !== "undefined") {
      await resolveComment(entityID, txID, message, "both")
      refreshDetails()
    }
  }

  async function addControlComment(message: string, forward: boolean) {
    if (typeof entityID !== "undefined") {
      await resolveControlComment(entityID, [txID], message, forward)
      refreshDetails()
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveDetails(entityID, txID)
    }
  }, [resolveDetails, entityID, txID])

  useEffect(() => {
    if (details.data) {
      reset(toTransactionFormState(details.data))
    }
  }, [tx, details.data, reset])

  return {
    form: data,
    hasChange,
    details,
    comment,
    fieldErrors,
    validationErrors,
    status,
    request,
    transaction: tx,
    change: onChange,
    submit,
    close,
    addComment,
    addControlComment,
    refreshDetails,
  }
}
