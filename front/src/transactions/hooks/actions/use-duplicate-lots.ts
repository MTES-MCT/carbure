import { useTranslation } from "react-i18next"
import { Entity } from "carbure/types"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { Transaction } from "common/types"

export interface LotDuplicator {
  loading: boolean
  duplicateLot: (tx: Transaction) => Promise<boolean>
}

export default function useDuplicateLot(
  entity: Entity,
  refresh: () => void
): LotDuplicator {
  const { t } = useTranslation()
  const notifications = useNotificationContext()
  const [request, resolveDuplicate] = useAPI(api.duplicateLot)

  async function duplicateLot(tx: Transaction) {
    const shouldDuplicate = await confirm(
      t("Dupliquer lot"),
      t("Voulez vous dupliquer ce lot ?")
    )

    if (entity !== null && shouldDuplicate) {
      const res = await resolveDuplicate(entity.id, tx.id)

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: t("Le lot a bien été dupliqué !"),
        })
      }
    }

    return shouldDuplicate
  }

  return { loading: request.loading, duplicateLot }
}
