import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "transactions/api"
import useAPI from "../helpers/use-api"

import { confirm } from "../../components/dialog"
import { useNotificationContext } from "../../components/notifications"

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
      const res = await resolveDuplicate(entity.id, lotID)

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le lot a bien été dupliqué !",
        })
      }
    }

    return shouldDuplicate
  }

  return { loading: request.loading, duplicateLot }
}
