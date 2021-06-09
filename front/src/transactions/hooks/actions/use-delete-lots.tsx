import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { Transaction, TransactionQuery } from "common/types"
import { SummaryPrompt } from "transactions/components/summary"

export interface LotDeleter {
  loading: boolean
  deleteLot: (tx: Transaction) => Promise<boolean>
  deleteSelection: () => Promise<boolean>
  deleteAll: () => Promise<boolean>
}

export default function useDeleteLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void,
  stock?: boolean
): LotDeleter {
  const notifications = useNotificationContext()

  const [request, resolveDelete] = useAPI(api.deleteLots)

  async function notifyDelete(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été supprimés !"
          : "Le lot a bien été supprimé !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible de supprimer les lots."
          : "Impossible de supprimer le lot.",
      })
    }
  }

  async function deleteLot(tx: Transaction) {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer ce lot ?"
    )

    if (entity !== null && shouldDelete) {
      await notifyDelete(resolveDelete(entity.id, [tx.id]))
    }

    return shouldDelete
  }

  async function deleteSelection() {
    const shouldDelete = await prompt<number[]>((resolve) => (
      <SummaryPrompt
        stock={stock}
        title="Supprimer lot"
        description="Voulez vous supprimer les lots sélectionnés ?"
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (entity !== null && shouldDelete) {
      await notifyDelete(resolveDelete(entity.id, selection.selected), true)
    }

    return Boolean(shouldDelete)
  }

  async function deleteAll() {
    if (entity !== null) {
      const allTxids = await prompt<number[]>((resolve) => (
        <SummaryPrompt
          stock={stock}
          title="Supprimer tous ces brouillons"
          description="Voulez vous supprimer tous ces lots ?"
          query={query}
          selection={selection.selected}
          onResolve={resolve}
        />
      ))

      if (entity !== null && allTxids) {
        await notifyDelete(resolveDelete(entity.id, allTxids), true)
      }

      return Boolean(allTxids)
    }

    return false
  }

  return {
    loading: request.loading,
    deleteLot,
    deleteSelection,
    deleteAll,
  }
}
