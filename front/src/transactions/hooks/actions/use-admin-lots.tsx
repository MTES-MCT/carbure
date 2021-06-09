import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { useNotificationContext } from "../../../common/components/notifications"
import { Transaction } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"

export interface LotAdministrator {
  loading: boolean
  markAsRead: (tx: Transaction) => Promise<boolean>
  markForReview: (tx: Transaction) => Promise<boolean>
  hideAlerts: (txIDs: number[]) => Promise<boolean>
  highlightAlerts: (txIDs: number[]) => Promise<boolean>
}

export default function useAdministrateLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  refresh: () => void
): LotAdministrator {
  const notifications = useNotificationContext()

  const [requestHide, resolveHideLots] = useAPI(api.hideAdminLots)
  const [requestHighlight, resolveHighlightLots] = useAPI(
    api.highlightAdminLots
  )
  const [requestHideAlert, resolveHideAlerts] = useAPI(api.postHideAlerts)
  const [requestHighlightAlert, resolveHighlightAlerts] = useAPI(
    api.postHighlightAlerts
  )

  async function notify(promise: Promise<any>) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: "Succès",
      })
    } else {
      notifications.push({
        level: "error",
        text: "Erreur",
      })
    }
  }

  async function markAsRead(tx: Transaction) {
    if (entity) {
      await notify(resolveHideLots(entity?.id, [tx.id]))
      return true
    }
    return false
  }

  async function markForReview(tx: Transaction) {
    if (entity) {
      await notify(resolveHighlightLots(entity?.id, [tx.id]))
      return true
    }
    return false
  }

  async function hideAlerts(alertIDs: number[]) {
    await notify(resolveHideAlerts(alertIDs))
    return true
  }

  async function highlightAlerts(alertIDs: number[]) {
    await notify(resolveHighlightAlerts(alertIDs))
    return true
  }

  return {
    loading:
      requestHide.loading ||
      requestHideAlert.loading ||
      requestHighlightAlert.loading ||
      requestHighlight.loading,
    markAsRead,
    markForReview,
    hideAlerts,
    highlightAlerts,
  }
}
