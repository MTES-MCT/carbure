import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm, prompt } from "../../components/system/dialog"

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
      "Voulez vous envoyer ce lot ?"
    )

    if (entity !== null && shouldValidate) {
      await resolveValidate(entity.id, [lotID]).then(refresh)
    }

    return shouldValidate
  }

  async function validateAndCommentLot(lotID: number) {
    const comment = await prompt(
      "Envoyer lot",
      "Voulez vous renvoyer ce lot corrigé ?"
    )

    if (entity !== null && comment) {
      await resolveValidateAndComment(entity.id, lotID, comment).then(refresh)
    }

    return Boolean(comment)
  }

  async function validateSelection() {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "Voulez vous envoyer les lots sélectionnés ?"
    )

    if (entity !== null && shouldValidate) {
      await resolveValidate(entity.id, selection.selected).then(refresh)
    }

    return shouldValidate
  }

  async function validateAllDrafts() {
    const shouldValidate = await confirm(
      "Envoyer lot",
      "Voulez vous envoyer tous ces lots ?"
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
