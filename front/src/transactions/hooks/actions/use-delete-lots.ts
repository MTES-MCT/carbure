import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"

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

  async function deleteAllDrafts() {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer tous ces lots ?"
    )

    if (entity !== null && shouldDelete) {
      await notifyDelete(resolveDeleteAll(entity.id, year.selected), true)
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
