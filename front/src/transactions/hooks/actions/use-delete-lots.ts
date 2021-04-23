import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { FilterSelection } from "../query/use-filters"
import { SpecialSelection } from "../query/use-special"
import { SearchSelection } from "../query/use-search"
import { LotStatus } from "common/types"

export interface LotDeleter {
  loading: boolean
  deleteLot: (l: number) => Promise<boolean>
  deleteSelection: () => Promise<boolean>
  deleteAll: () => Promise<boolean>
}

export default function useDeleteLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  filters: FilterSelection,
  year: YearSelection,
  search: SearchSelection,
  special: SpecialSelection,
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
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer les lots sélectionnés ?"
    )

    if (entity !== null && shouldDelete) {
      await notifyDelete(resolveDelete(entity.id, selection.selected), true)
    }

    return shouldDelete
  }

  async function deleteAll() {
    if (entity !== null) {
      const filteredDrafts = await api.getLots(LotStatus.Draft, entity.id, filters["selected"], year.selected, 0, null, search.query, 'id', 'asc', special.invalid, special.deadline) // prettier-ignore
      const nbClients = new Set(
        filteredDrafts.lots.map((o) => o.carbure_client ? o.carbure_client.name : o.unknown_client)
      ).size
      const totalVolume = filteredDrafts.lots
        .map((o) => o.lot.volume)
        .reduce((sum, vol) => sum + vol)
      const clientsStr = nbClients > 1 ? "clients" : "client"
      const allTxids = filteredDrafts.lots.map((o) => o.id)

      const shouldDelete = await confirm(
        "Supprimer tous ces brouillons",
        `Voulez êtes sur le point de supprimer ${filteredDrafts.lots.length} lots concernant ${nbClients} ${clientsStr} pour un total de ${totalVolume} litres`
      )

      if (entity !== null && shouldDelete) {
        await notifyDelete(resolveDelete(entity.id, allTxids), true)
      }
      return shouldDelete
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
