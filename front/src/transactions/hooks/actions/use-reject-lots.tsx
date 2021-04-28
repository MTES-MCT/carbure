import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"
import { getStocks } from "stocks/api"

import { prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import {
  CommentPrompt,
  CommentWithSummaryPrompt,
} from "transactions/components/form-comments"
import { EntityType, TransactionQuery } from "common/types"

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
    const comment = await prompt<string>((resolve) => (
      <CommentWithSummaryPrompt
        title="Refuser lot"
        description="Voulez vous refuser les lots sélectionnés ?"
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (entity !== null && comment) {
      await notifyReject(
        resolveReject(entity.id, selection.selected, comment),
        true
      )
    }

    return Boolean(comment)
  }

  async function rejectAllInbox() {
    if (entity !== null) {
      // getLots with current filters but no limit
      // display summary (number of lots, number of suppliers
      // call AcceptLots with all the tx_ids
      var allInboxLots
      if (entity.entity_type === EntityType.Operator) {
        allInboxLots = await api.getLots({ ...query, limit: null })
      } else {
        allInboxLots = await getStocks(
          entity.id,
          query,
          "in",
          0,
          null,
          query.query
        )
      }
      const nbSuppliers = new Set(
        allInboxLots.lots.map((o) => o.carbure_vendor?.name)
      ).size
      const totalVolume = allInboxLots.lots
        .map((o) => o.lot.volume)
        .reduce((sum, vol) => sum + vol)
      const supplierStr = nbSuppliers > 1 ? "fournisseurs" : "fournisseur"
      const allTxids = allInboxLots.lots.map((o) => o.id)
      const description = `Vous êtes sur le point de refuser ${allInboxLots.lots.length} lots de ${nbSuppliers} ${supplierStr} représentant un total de ${totalVolume} litres`

      const comment = await prompt<string>((resolve) => (
        <CommentWithSummaryPrompt
          title="Refuser tout"
          description={description}
          query={query}
          selection={selection.selected}
          onResolve={resolve}
        />
      ))

      if (comment) {
        await notifyReject(resolveReject(entity.id, allTxids, comment), true)
      }

      return Boolean(comment)
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
