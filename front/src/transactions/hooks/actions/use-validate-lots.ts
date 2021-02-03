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

      if (res.valid > 0) {
        notifications.push({
          level: "success",
          text:
            res.submitted === 1
              ? "Le lot a bien été envoyé !"
              : `${res.valid} lots sur ${res.submitted} ont bien été envoyés !`,
        })
      }

      if (res.invalid > 0) {
        notifications.push({
          level: "error",
          text:
            res.submitted === 1
              ? "Le lot n'a pas pu être validé !"
              : `${res.invalid} lots sur ${res.submitted} n'ont pas pu être validés !`,
        })
      }

      if (res.duplicates > 0) {
        notifications.push({
          level: "warning",
          text:
            res.submitted === 1
              ? "Un double du lot a été détecté dans la base de données !"
              : `${res.duplicates} sont des doubles de lots existants !`,
        })
      }
    } else {
      notifications.push({
        level: "error",
        text: "Échec de la validation",
      })
    }
  }

  async function validateLot(lotID: number) {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "En envoyant ce lot, je certifie qu'il respecte les critères du durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      await notifyValidate(resolveValidate(entity.id, [lotID]))
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
      await notifyValidate(resolveValidateAndComment(entity.id, lotID, comment))
    }

    return Boolean(comment)
  }

  async function validateSelection() {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "En envoyant les lots suivants, je certifie qu'ils respectent les critères de durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      await notifyValidate(resolveValidate(entity.id, selection.selected), true)
    }

    return shouldValidate
  }

  async function validateAllDrafts() {
    const shouldValidate = await confirm(
      "Envoyer tous les brouillons",
      "En envoyant ces lots, je certifie qu'ils respectent les critères du durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      await notifyValidate(resolveValidateAll(entity.id, year.selected), true)
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
