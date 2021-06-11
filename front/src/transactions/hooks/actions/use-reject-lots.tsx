import { useTranslation } from "react-i18next"
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
import { Transaction, TransactionQuery } from "common/types"

export interface LotRejector {
  loading: boolean
  rejectLot: (tx: Transaction) => Promise<boolean>
  rejectSelection: () => Promise<boolean>
  rejectAllInbox: () => Promise<boolean>
}

export default function useRejectLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void,
  stock?: boolean
): LotRejector {
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const [request, resolveReject] = useAPI(api.rejectLots)

  async function notifyReject(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? t("Les lots ont bien été refusés !")
          : t("Le lot a bien été refusé !"),
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? t("Impossible de refuser les lots.")
          : t("Impossible de refuser le lot."),
      })
    }
  }

  async function rejectLot(tx: Transaction) {
    const comment = await prompt<string>((resolve) => (
      <CommentPrompt
        title={t("Refuser lot")}
        description={t("Voulez vous refuser ce lot ?")}
        onResolve={resolve}
      />
    ))

    if (entity !== null && comment) {
      await notifyReject(resolveReject(entity.id, [tx.id], comment))
    }

    return Boolean(comment)
  }

  async function rejectSelection() {
    const res = await prompt<[string, number[]]>((resolve) => (
      <CommentWithSummaryPrompt
        stock={stock}
        title={t("Refuser lot")}
        description={t("Voulez vous refuser les lots sélectionnés ?")}
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
          stock={stock}
          title={t("Refuser tout")}
          description={t("Voulez vous refuser tous ces lots ?")}
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
