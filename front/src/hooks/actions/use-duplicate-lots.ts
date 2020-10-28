import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm } from "../../components/system/dialog"

export interface LotDuplicator {
  loading: boolean
  duplicateLot: (i: number) => void
}

export default function useDuplicateLot(
  entity: EntitySelection,
  refresh: () => void
): LotDuplicator {
  const [request, resolveDuplicate] = useAPI(api.duplicateLot)

  async function duplicateLot(lotID: number) {
    const shouldDuplicate = await confirm(
      "Dupliquer lots",
      "Voulez vous dupliquer ce lot ?"
    )

    if (entity !== null && shouldDuplicate) {
      resolveDuplicate(entity.id, lotID).then(refresh)
    }
  }

  return { loading: request.loading, duplicateLot }
}
