import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { useNotificationContext } from "../../../common/components/notifications"
import { Transaction } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { useTranslation } from "react-i18next"
import { confirm, prompt } from "common/components/dialog"
import { PinPrompt } from "transactions/components/pin"

export interface LotAdministrator {
  loading: boolean
  markAsRead: (tx: Transaction) => Promise<boolean>
  markForReview: (tx: Transaction) => Promise<boolean>
  markSelectionAsRead: () => Promise<boolean>
  markSelectionForReview: () => Promise<boolean>
  hideAlerts: (txIDs: number[]) => Promise<boolean>
  highlightAlerts: (txIDs: number[]) => Promise<boolean>
}

export default function useAdministrateLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  refresh: () => void
): LotAdministrator {
  const { t } = useTranslation()
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
        text: t("Le lot a bien été mis à jour"),
      })
    } else {
      notifications.push({
        level: "error",
        text: t("L'opération a échoué"),
      })
    }
  }

  async function hideAlerts(alertIDs: number[]) {
    await notify(resolveHideAlerts(alertIDs))
    return true
  }

  async function highlightAlerts(alertIDs: number[]) {
    await notify(resolveHighlightAlerts(alertIDs))
    return true
  }

  async function markAsRead(tx: Transaction) {
    const shouldHide = tx.hidden_by_admin
      ? await confirm(
          t("Montrer le lot"),
          t("Voulez-vous montrer à nouveau ce lot dans la liste ?")
        )
      : await confirm(
          t("Ignorer le lot"),
          t("Voulez-vous ne plus voir ce lot dans la liste ?")
        )

    if (entity !== null && shouldHide) {
      await notify(resolveHideLots(entity.id, [tx.id]))
    }

    return shouldHide
  }

  async function markSelectionAsRead() {
    const shouldHide = await confirm(
      t("Ignorer la sélection"),
      t("Voulez-vous ne plus voir les lots sélectionnés dans la liste ?")
    )

    if (entity !== null && shouldHide) {
      await notify(resolveHideLots(entity.id, selection.selected))
    }

    return shouldHide
  }

  async function markForReview(tx: Transaction) {
    if (entity === null) return false

    if (tx.highlighted_by_admin) {
      const shouldHighlight = await confirm(
        t("Désépingler le lot"),
        t("Voulez-vous retirer ce lot de la liste des lots mis de côté ?")
      )

      if (shouldHighlight) {
        await notify(resolveHighlightLots(entity.id, [tx.id]))
      }

      return Boolean(shouldHighlight)
    } else {
      const shouldHighlight = await prompt<boolean>((resolve) => (
        <PinPrompt
          role="admin"
          title={t("Épingler ce lot")}
          description={t(
            "Voulez-vous mettre ce lot de côté pour l'étudier plus tard ?"
          )}
          onResolve={resolve}
        />
      ))

      if (typeof shouldHighlight === "boolean") {
        await notify(resolveHighlightLots(entity.id, [tx.id], shouldHighlight))
      }

      return Boolean(shouldHighlight)
    }
  }

  async function markSelectionForReview() {
    if (!entity) return false

    const shouldHighlight = await prompt<boolean>((resolve) => (
      <PinPrompt
        role="admin"
        title={t("Épingler la sélection")}
        description={t(
          "Voulez-vous mettre les lots sélectionnés de côté pour les étudier plus tard  ?"
        )}
        onResolve={resolve}
      />
    ))

    if (typeof shouldHighlight === "boolean") {
      await notify(
        resolveHighlightLots(entity.id, selection.selected, shouldHighlight)
      )
    }

    return Boolean(shouldHighlight)
  }

  return {
    loading:
      requestHide.loading ||
      requestHideAlert.loading ||
      requestHighlightAlert.loading ||
      requestHighlight.loading,
    markAsRead,
    markSelectionAsRead,
    markForReview,
    markSelectionForReview,
    hideAlerts,
    highlightAlerts,
  }
}
