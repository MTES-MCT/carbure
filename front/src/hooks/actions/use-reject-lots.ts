import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { prompt } from "../../components/system/dialog"

export interface LotRejector {
  loading: boolean
  rejectLot: (l: number) => void
  rejectSelection: () => void
  rejectAllInbox: () => void
}

export default function useRejectLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): LotRejector {
  const [request, resolveReject] = useAPI(api.rejectLots)
  const [requestAll, resolveRejectAll] = useAPI(api.rejectAllInboxLots)

  async function rejectLot(lotID: number) {
    const comment = await prompt("Refuser lots", "Voulez vous refuser ce lot ?")

    if (entity !== null && comment) {
      resolveReject(entity.id, [lotID], comment).then(refresh)
    }
  }

  async function rejectSelection() {
    const comment = await prompt(
      "Refuser lots",
      "Voulez vous refuser les lots sélectionnés ?"
    )

    if (entity !== null && comment) {
      resolveReject(entity.id, selection.selected, comment).then(refresh)
    }
  }

  async function rejectAllInbox() {
    const comment = await prompt(
      "Refuser lots",
      "Voulez vous refuser tous ces lots ?"
    )

    if (entity !== null && comment) {
      resolveRejectAll(entity.id, year.selected, comment).then(refresh)
    }
  }

  return {
    loading: request.loading || requestAll.loading,
    rejectLot,
    rejectSelection,
    rejectAllInbox,
  }
}
