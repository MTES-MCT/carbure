import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm } from "../../components/system/dialog"
import { useNotificationContext } from "../../components/system/notifications"

export interface LotDeleter {
  loading: boolean
  deleteLot: (l: number) => Promise<boolean>
  deleteSelection: () => Promise<boolean>
  deleteAllDrafts: () => Promise<boolean>
}

export default function useDeleteLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): LotDeleter {
  const notifications = useNotificationContext()

  const [request, resolveDelete] = useAPI(api.deleteLots)
  const [requestAll, resolveDeleteAll] = useAPI(api.deleteAllDraftLots)

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
          ? "Impossible de supprimer certains de ces lots."
          : "Impossible de supprimer ce lot.",
      })
    }
  }

  async function deleteLot(lotID: number) {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer ce lot ?"
    )

    if (entity !== null && shouldDelete) {
      notifyDelete(resolveDelete(entity.id, [lotID]))
    }

    return shouldDelete
  }

  async function deleteSelection() {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer les lots sélectionnés ?"
    )

    if (entity !== null && shouldDelete) {
      notifyDelete(resolveDelete(entity.id, selection.selected), true)
    }

    return shouldDelete
  }

  async function deleteAllDrafts() {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer tous ces lots ?"
    )

    if (entity !== null && shouldDelete) {
      notifyDelete(resolveDeleteAll(entity.id, year.selected), true)
    }

    return shouldDelete
  }

  return {
    loading: request.loading || requestAll.loading,
    deleteLot,
    deleteSelection,
    deleteAllDrafts,
  }
}
