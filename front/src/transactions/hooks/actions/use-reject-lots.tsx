import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import {
  CommentPrompt,
  CommentWithSummaryPrompt,
} from "transactions/components/form-comments"
import { TransactionQuery } from "common/types"

export interface LotRejector {
  loading: boolean
  rejectLot: (l: number) => Promise<boolean>
  rejectSelection: () => Promise<boolean>
  rejectAllInbox: () => Promise<boolean>
}

export default function useRejectLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void
): LotRejector {
  const notifications = useNotificationContext()

  const [request, resolveReject] = useAPI(api.rejectLots)

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
    const comment = await prompt<string>((resolve) => (
      <CommentPrompt
        title="Refuser lot"
        description="Voulez vous refuser ce lot ?"
        onResolve={resolve}
      />
    ))

    if (entity !== null && comment) {
      await notifyReject(resolveReject(entity.id, [lotID], comment))
    }

    return Boolean(comment)
  }

  async function rejectSelection() {
    const res = await prompt<[string, number[]]>((resolve) => (
      <CommentWithSummaryPrompt
        title="Refuser lot"
        description="Voulez vous refuser les lots sélectionnés ?"
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (entity !== null && res) {
      await notifyReject(
        resolveReject(entity.id, selection.selected, res[0]),
        true
      )
    }

    return Boolean(res)
  }

  async function rejectAllInbox() {
    if (entity !== null) {
      const res = await prompt<[string, number[]]>((resolve) => (
        <CommentWithSummaryPrompt
          title="Refuser tout"
          description="Voulez vous refuser tous ces lots ?"
          query={query}
          selection={selection.selected}
          onResolve={resolve}
        />
      ))

      if (res) {
        const [comment, allTxids] = res
        await notifyReject(resolveReject(entity.id, allTxids, comment), true)
      }

      return Boolean(res)
    }
    return false
  }

  return {
    loading: request.loading,
    rejectLot,
    rejectSelection,
    rejectAllInbox,
  }
}
