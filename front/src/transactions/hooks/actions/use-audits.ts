import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "transactions/api"
import useAPI from "common/hooks/use-api"

import { confirm } from "common/components/dialog"
import { useNotificationContext } from "common/components/notifications"
import { Transaction } from "common/types"
import { TransactionSelection } from "../query/use-selection"

export interface LotAuditor {
  loading: boolean
  hideLot: (tx: Transaction) => Promise<boolean>
  hideLotSelection: () => Promise<boolean>
  highlightLot: (tx: Transaction) => Promise<boolean>
  highlightLotSelection: () => Promise<boolean>
}

export default function useAuditLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  refresh: () => void
): LotAuditor {
  const notifications = useNotificationContext()
  const [hideReq, resolveHideLot] = useAPI(api.hideAuditorLots)
  const [highlightReq, resolveHighlightLot] = useAPI(api.highlightAuditorLots)

  async function notify(promise: Promise<any>) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: "Le lot a bien été mis à jour",
      })
    } else {
      notifications.push({
        level: "error",
        text: "L'opération a échoué",
      })
    }
  }

  async function hideLot(tx: Transaction) {
    const shouldHide = tx.hidden_by_auditor
      ? await confirm(
          "Montrer le lot",
          "Voulez-vous montrer à nouveau ce lot dans la liste ?"
        )
      : await confirm(
          "Ignorer le lot",
          "Voulez-vous ne plus voir ce lot dans la liste ?"
        )

    if (entity !== null && shouldHide) {
      await notify(resolveHideLot(entity.id, [tx.id]))
    }

    return shouldHide
  }

  async function hideLotSelection() {
    const shouldHide = await confirm(
      "Ignorer la sélection",
      "Voulez-vous ne plus voir les lots sélectionnés dans la liste ?"
    )

    if (entity !== null && shouldHide) {
      await notify(resolveHideLot(entity.id, selection.selected))
    }

    return shouldHide
  }

  async function highlightLot(tx: Transaction) {
    const shouldHighlight = tx.highlighted_by_auditor
      ? await confirm(
          "Désépingler le lot",
          "Voulez-vous retirer ce lot de la liste des lots mis de côté ?"
        )
      : await confirm(
          "Épingler ce lot",
          "Voulez-vous mettre ce lot de côté pour l'étudier plus tard ?"
        )

    if (entity !== null && shouldHighlight) {
      await notify(resolveHighlightLot(entity.id, [tx.id]))
    }

    return shouldHighlight
  }

  async function highlightLotSelection() {
    const shouldHide = await confirm(
      "Épingler la sélection",
      "Voulez-vous mettre les lots sélectionnés de côté pour les étudier plus tard  ?"
    )

    if (entity !== null && shouldHide) {
      await notify(resolveHighlightLot(entity.id, selection.selected))
    }

    return shouldHide
  }

  return {
    loading: hideReq.loading && highlightReq.loading,
    hideLot,
    hideLotSelection,
    highlightLot,
    highlightLotSelection,
  }
}
