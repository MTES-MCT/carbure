import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { CommentPrompt } from "transactions/components/form-comments"

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
  const notifications = useNotificationContext()

  const [request, resolveReject] = useAPI(api.rejectLots)
  const [requestAll, resolveRejectAll] = useAPI(api.rejectAllInboxLots)

  async function notifyReject(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été refusés !"
          : "Le lot a bien été refusé !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible de refuser les lots."
          : "Impossible de refuser le lot.",
      })
    }
  }

  async function rejectLot(lotID: number) {
    const comment = await prompt(
      "Refuser lot",
      "Voulez vous refuser ce lot ?",
      CommentPrompt
    )

    if (entity !== null && comment) {
      notifyReject(resolveReject(entity.id, [lotID], comment))
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
      notifyReject(resolveReject(entity.id, selection.selected, comment), true)
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
      notifyReject(resolveRejectAll(entity.id, year.selected, comment), true)
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
