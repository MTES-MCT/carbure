import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import { getStocks } from "stocks/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import {
  CommentWithTypePrompt,
  CommentWithType,
} from "transactions/components/form-comments"
import { EntityType, TransactionQuery } from "common/types"
import { SummaryPrompt } from "transactions/components/summary"

export interface LotAcceptor {
  loading: boolean
  acceptLot: (l: number) => Promise<boolean>
  acceptAndCommentLot: (l: number) => Promise<boolean>
  acceptSelection: () => Promise<boolean>
  acceptAllInbox: () => Promise<boolean>
}

export default function useAcceptLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void
): LotAcceptor {
  const notifications = useNotificationContext()

  const [request, resolveAccept] = useAPI(api.acceptLots)
  const [requestComment, resolveAcceptAndComment] = useAPI(api.acceptAndCommentLot) // prettier-ignore

  async function notifyAccept(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été acceptés !"
          : "Le lot a bien été accepté !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible d'accepter les lots."
          : "Impossible d'accepter le lot.",
      })
    }
  }

  async function acceptLot(lotID: number) {
    const shouldAccept = await confirm(
      "Accepter lot",
      "Voulez vous accepter ce lot ?"
    )

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAccept(entity.id, [lotID]))
    }

    return shouldAccept
  }

  async function acceptAndCommentLot(lotID: number) {
    const result = await prompt<CommentWithType>((resolve) => (
      <CommentWithTypePrompt onResolve={resolve} />
    ))

    if (entity !== null && result) {
      await notifyAccept(
        resolveAcceptAndComment(entity.id, lotID, result.comment, result.topic)
      )
    }

    return Boolean(result)
  }

  async function acceptSelection() {
    const shouldAccept = await prompt<boolean>((resolve) => (
      <SummaryPrompt
        title="Accepter lot"
        description="Voulez vous accepter les lots sélectionnés ?"
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAccept(entity.id, selection.selected), true)
    }

    return Boolean(shouldAccept)
  }

  async function acceptAllInbox() {
    if (entity !== null) {
      // getLots with current filters but no limit
      // display summary (number of lots, number of suppliers
      // call AcceptLots with all the tx_ids
      let allInboxLots =
        entity.entity_type === EntityType.Operator
          ? await api.getLots({ ...query, limit: null })
          : await getStocks(entity.id, query, "in", 0, null, query.query)

      const nbSuppliers = new Set(
        allInboxLots.lots.map((o) => o.carbure_vendor?.name)
      ).size
      const totalVolume = allInboxLots.lots
        .map((o) => o.lot.volume)
        .reduce((sum, vol) => sum + vol)
      const supplierStr = nbSuppliers > 1 ? "fournisseurs" : "fournisseur"
      const allTxids = allInboxLots.lots.map((o) => o.id)

      const shouldAccept = await prompt<boolean>((resolve) => (
        <SummaryPrompt
          title="Accepter tout"
          description={`Voulez êtes sur le point d'accepter ${allInboxLots.lots.length} lots de ${nbSuppliers} ${supplierStr} représentant un total de ${totalVolume} litres ?`}
          query={query}
          selection={selection.selected}
          onResolve={resolve}
        />
      ))

      if (entity !== null && shouldAccept) {
        await notifyAccept(resolveAccept(entity.id, allTxids), true)
      }

      return Boolean(shouldAccept)
    }

    return false
  }

  return {
    loading: request.loading || requestComment.loading,
    acceptLot,
    acceptAndCommentLot,
    acceptSelection,
    acceptAllInbox,
  }
}
