import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import confirm from "../../components/system/confirm"

export interface LotDeleter {
  loading: boolean
  deleteLot: (l: number) => void
  deleteSelection: () => void
  deleteAllDrafts: () => void
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
      "Supprimer lots",
      "Voulez vous supprimer ce lot ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDelete(entity.id, [lotID]).then(refresh)
    }
  }

  async function deleteSelection() {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer les lots sélectionnés ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDelete(entity.id, selection.selected).then(refresh)
    }
  }

  async function deleteAllDrafts() {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer tous ces lots ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDeleteAll(entity.id, year.selected).then(refresh)
    }
  }

  return {
    loading: request.loading || requestAll.loading,
    deleteLot,
    deleteSelection,
    deleteAllDrafts,
  }
}
