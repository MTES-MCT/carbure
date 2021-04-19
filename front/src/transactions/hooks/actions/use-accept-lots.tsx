import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import {
  CommentWithTypePrompt,
  CommentWithType,
} from "transactions/components/form-comments"
import { SpecialSelection } from "../query/use-special"
import { FilterSelection } from "../query/use-filters"
import { SearchSelection } from "../query/use-search"
import { LotStatus } from "common/types"

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
  filters: FilterSelection,
  year: YearSelection,
  search: SearchSelection,
  special: SpecialSelection,
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
    const shouldAccept = await confirm(
      "Accepter lot",
      "Voulez vous accepter les lots sélectionnés ?"
    )

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAccept(entity.id, selection.selected), true)
    }

    return shouldAccept
  }

  async function acceptAllInbox() {
    if (entity !== null) {
      // getLots with current filters but no limit
      // display summary (number of lots, number of suppliers
      // call AcceptLots with all the tx_ids
      const allInboxLots = await api.getLots(LotStatus.Inbox, entity.id, filters["selected"], year.selected, 0, null, search.query, 'id', 'asc', special.invalid, special.deadline)
      const nbSuppliers = new Set(allInboxLots.lots.map(o => o.carbure_vendor?.name)).size
      const totalVolume = allInboxLots.lots.map(o => o.lot.volume).reduce((sum, vol) => sum + vol)
      const supplierStr = nbSuppliers > 1 ? "fournisseurs" : "fournisseur"
      const allTxids = allInboxLots.lots.map(o => o.id)

      const shouldAccept = await confirm(
        "Accepter Tout",
        `Voulez êtes sur le point d'accepter ${allInboxLots.lots.length} lots de ${nbSuppliers} ${supplierStr} représentant un total de ${totalVolume} litres ?`
      )
   
      if (entity !== null && shouldAccept) {
        await notifyAccept(resolveAccept(entity.id, allTxids), true)
      }
      return shouldAccept
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
