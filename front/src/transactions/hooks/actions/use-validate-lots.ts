import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { CommentPrompt } from "transactions/components/form-comments"

export interface LotValidator {
  loading: boolean
  validateLot: (l: number) => Promise<boolean>
  validateAndCommentLot: (l: number) => Promise<boolean>
  validateSelection: () => Promise<boolean>
  validateAllDrafts: () => Promise<boolean>
}

export default function useValidateLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): LotValidator {
  const notifications = useNotificationContext()

  const [request, resolveValidate] = useAPI(api.validateLots)
  const [requestComment, resolveValidateAndComment] = useAPI(api.validateAndCommentLot) // prettier-ignore
  const [requestAll, resolveValidateAll] = useAPI(api.validateAllDraftLots)

  async function notifyValidate(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été envoyés !"
          : "Le lot a bien été envoyé !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible d'envoyer les lots."
          : "Impossible d'envoyer le lot.",
      })
    }
  }

  async function validateLot(lotID: number) {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "En envoyant ce lot, je certifie qu'il respecte les critères du durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      notifyValidate(resolveValidate(entity.id, [lotID]))
    }

    return shouldValidate
  }

  async function validateAndCommentLot(lotID: number) {
    const comment = await prompt(
      "Envoyer lot",
      "Voulez vous renvoyer ce lot corrigé ?",
      CommentPrompt
    )

    if (entity !== null && comment) {
      notifyValidate(resolveValidateAndComment(entity.id, lotID, comment))
    }

    return Boolean(comment)
  }

  async function validateSelection() {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "En envoyant les lots suivants, je certifie qu'ils respectent les critères de durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      notifyValidate(resolveValidate(entity.id, selection.selected), true)
    }

    return shouldValidate
  }

  async function validateAllDrafts() {
    const shouldValidate = await confirm(
      "Envoyer tous les brouillons",
      "En envoyant ces lots, je certifie qu'ils respectent les critères du durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      notifyValidate(resolveValidateAll(entity.id, year.selected), true)
    }

    return shouldValidate
  }

  return {
    loading: request.loading || requestAll.loading || requestComment.loading,
    validateLot,
    validateAndCommentLot,
    validateSelection,
    validateAllDrafts,
  }
}
