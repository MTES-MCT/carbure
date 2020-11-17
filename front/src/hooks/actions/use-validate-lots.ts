import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm, prompt } from "../../components/system/dialog"
import { CommentPrompt } from "../../components/comments"

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
  const [request, resolveValidate] = useAPI(api.validateLots)
  const [requestComment, resolveValidateAndComment] = useAPI(api.validateAndCommentLot) // prettier-ignore
  const [requestAll, resolveValidateAll] = useAPI(api.validateAllDraftLots)

  async function validateLot(lotID: number) {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "En envoyant ce lot, je certifie qu'il respecte les critères du durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      await resolveValidate(entity.id, [lotID]).then(refresh)
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
      await resolveValidateAndComment(entity.id, lotID, comment).then(refresh)
    }

    return Boolean(comment)
  }

  async function validateSelection() {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "En envoyant les lots suivants, je certifie qu'ils respectent les critères de durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      await resolveValidate(entity.id, selection.selected).then(refresh)
    }

    return shouldValidate
  }

  async function validateAllDrafts() {
    const shouldValidate = await confirm(
      "Envoyer tous les brouillons",
      "En envoyant ces lots, je certifie qu'ils respectent les critères du durabilité liés aux terres et que les informations renseignées sont réelles et valides"
    )

    if (entity !== null && shouldValidate) {
      await resolveValidateAll(entity.id, year.selected).then(refresh)
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
