import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm } from "../../components/system/dialog"

export interface LotDuplicator {
  loading: boolean
  duplicateLot: (i: number) => Promise<boolean>
}

export default function useDuplicateLot(
  entity: EntitySelection,
  refresh: () => void
): LotDuplicator {
  const [request, resolveDuplicate] = useAPI(api.duplicateLot)

  async function duplicateLot(lotID: number) {
    const shouldDuplicate = await confirm(
      "Dupliquer lot",
      "Voulez vous dupliquer ce lot ?"
    )

    if (entity !== null && shouldDuplicate) {
      await resolveDuplicate(entity.id, lotID).then(refresh)
    }

    return shouldDuplicate
  }

  return { loading: request.loading, duplicateLot }
}
