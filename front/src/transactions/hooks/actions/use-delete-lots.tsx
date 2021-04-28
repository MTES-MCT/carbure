import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { TransactionQuery } from "common/types"
import { SummaryPrompt } from "transactions/components/summary"

export interface LotDeleter {
  loading: boolean
  deleteLot: (l: number) => Promise<boolean>
  deleteSelection: () => Promise<boolean>
  deleteAll: () => Promise<boolean>
}

export default function useDeleteLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void
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

  async function deleteLot(lotID: number) {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer ce lot ?"
    )

    if (entity !== null && shouldDelete) {
      await notifyDelete(resolveDelete(entity.id, [lotID]))
    }

    return shouldDelete
  }

  async function deleteSelection() {
    const shouldDelete = await prompt<boolean>((resolve) => (
      <SummaryPrompt
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
      const filteredDrafts = await api.getLots(query)
      const nbClients = new Set(
        filteredDrafts.lots.map((o) =>
          o.carbure_client ? o.carbure_client.name : o.unknown_client
        )
      ).size
      const totalVolume = filteredDrafts.lots
        .map((o) => o.lot.volume)
        .reduce((sum, vol) => sum + vol, 0)
      const clientsStr = nbClients > 1 ? "clients" : "client"
      const allTxids = filteredDrafts.lots.map((o) => o.id)

      const shouldDelete = await prompt<boolean>((resolve) => (
        <SummaryPrompt
          title="Supprimer tous ces brouillons"
          description={`Voulez êtes sur le point de supprimer ${filteredDrafts.lots.length} lots concernant ${nbClients} ${clientsStr} pour un total de ${totalVolume} litres`}
          query={query}
          selection={selection.selected}
          onResolve={resolve}
        />
      ))

      if (entity !== null && shouldDelete) {
        await notifyDelete(resolveDelete(entity.id, allTxids), true)
      }

      return Boolean(shouldDelete)
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
