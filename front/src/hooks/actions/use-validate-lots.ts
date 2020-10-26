import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import confirm from "../../components/system/confirm"

export interface LotValidator {
  loading: boolean
  validateLot: (l: number) => void
  validateSelection: () => void
  validateAllDrafts: () => void
}

export default function useValidateLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): LotValidator {
  const [request, resolveValidate] = useAPI(api.validateLots)
  const [requestAll, resolveValidateAll] = useAPI(api.validateAllDraftLots)

  async function validateLot(lotID: number) {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer ce lot ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidate(entity.id, [lotID]).then(refresh)
    }
  }

  async function validateSelection() {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer les lots sélectionnés ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidate(entity.id, selection.selected).then(refresh)
    }
  }

  async function validateAllDrafts() {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer tous ces lots ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidateAll(entity.id, year.selected).then(refresh)
    }
  }

  return {
    loading: request.loading || requestAll.loading,
    validateLot,
    validateSelection,
    validateAllDrafts,
  }
}
