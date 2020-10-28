import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm } from "../../components/system/dialog"

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
  const [request, resolveDelete] = useAPI(api.deleteLots)
  const [requestAll, resolveDeleteAll] = useAPI(api.deleteAllDraftLots)

  async function deleteLot(lotID: number) {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer ce lot ?"
    )

    if (entity !== null && shouldDelete) {
      await resolveDelete(entity.id, [lotID]).then(refresh)
    }

    return shouldDelete
  }

  async function deleteSelection() {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer les lots sélectionnés ?"
    )

    if (entity !== null && shouldDelete) {
      await resolveDelete(entity.id, selection.selected).then(refresh)
    }

    return shouldDelete
  }

  async function deleteAllDrafts() {
    const shouldDelete = await confirm(
      "Supprimer lot",
      "Voulez vous supprimer tous ces lots ?"
    )

    if (entity !== null && shouldDelete) {
      await resolveDeleteAll(entity.id, year.selected).then(refresh)
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
