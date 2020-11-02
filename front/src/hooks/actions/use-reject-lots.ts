import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { prompt } from "../../components/system/dialog"
import { CommentPrompt } from "../../components/comments"

export interface LotRejector {
  loading: boolean
  rejectLot: (l: number) => Promise<boolean>
  rejectSelection: () => Promise<boolean>
  rejectAllInbox: () => Promise<boolean>
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
    const comment = await prompt(
      "Refuser lot",
      "Voulez vous refuser ce lot ?",
      CommentPrompt
    )

    if (entity !== null && comment) {
      resolveReject(entity.id, [lotID], comment).then(refresh)
    }

    return Boolean(comment)
  }

  async function rejectSelection() {
    const comment = await prompt(
      "Refuser lot",
      "Voulez vous refuser les lots sélectionnés ?",
      CommentPrompt
    )

    if (entity !== null && comment) {
      await resolveReject(entity.id, selection.selected, comment).then(refresh)
    }

    return Boolean(comment)
  }

  async function rejectAllInbox() {
    const comment = await prompt(
      "Refuser lot",
      "Voulez vous refuser tous ces lots ?",
      CommentPrompt
    )

    if (entity !== null && comment) {
      await resolveRejectAll(entity.id, year.selected, comment).then(refresh)
    }

    return Boolean(comment)
  }

  return {
    loading: request.loading || requestAll.loading,
    rejectLot,
    rejectSelection,
    rejectAllInbox,
  }
}
