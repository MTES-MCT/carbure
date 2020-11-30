import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm } from "../../components/system/dialog"
import { useNotificationContext } from "../../components/system/notifications"

export interface LotDuplicator {
  loading: boolean
  duplicateLot: (i: number) => Promise<boolean>
}

export default function useDuplicateLot(
  entity: EntitySelection,
  refresh: () => void
): LotDuplicator {
  const notifications = useNotificationContext()
  const [request, resolveDuplicate] = useAPI(api.duplicateLot)

  async function duplicateLot(lotID: number) {
    const shouldDuplicate = await confirm(
      "Dupliquer lot",
      "Voulez vous dupliquer ce lot ?"
    )

    if (entity !== null && shouldDuplicate) {
      await resolveDuplicate(entity.id, lotID)

      refresh()

      notifications.push({
        level: "success",
        text: "Le lot a bien été dupliqué !",
      })
    }

    return shouldDuplicate
  }

  return { loading: request.loading, duplicateLot }
}
