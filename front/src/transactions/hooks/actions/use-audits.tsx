import { useTranslation } from "react-i18next"
import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "transactions/api"
import useAPI from "common/hooks/use-api"

import { confirm, prompt } from "common/components/dialog"
import { useNotificationContext } from "common/components/notifications"
import { Transaction } from "common/types"
import { TransactionSelection } from "../query/use-selection"
import { PinPrompt, PinConfig } from "transactions/components/pin"

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
  const { t } = useTranslation()
  const notifications = useNotificationContext()
  const [hideReq, resolveHideLot] = useAPI(api.hideAuditorLots)
  const [highlightReq, resolveHighlightLots] = useAPI(api.highlightAuditorLots)
  const [commentReq, addAuditorComment] = useAPI(api.addAuditorComment)

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

  async function hideLot(tx: Transaction) {
    const shouldHide = tx.hidden_by_auditor
      ? await confirm(
          t("Montrer le lot"),
          t("Voulez-vous montrer à nouveau ce lot dans la liste ?")
        )
      : await confirm(
          t("Ignorer le lot"),
          t("Voulez-vous ne plus voir ce lot dans la liste ?")
        )

    if (entity !== null && shouldHide) {
      await notify(resolveHideLot(entity.id, [tx.id]))
    }

    return shouldHide
  }

  async function hideLotSelection() {
    const shouldHide = await confirm(
      t("Ignorer la sélection"),
      t("Voulez-vous ne plus voir les lots sélectionnés dans la liste ?")
    )

    if (entity !== null && shouldHide) {
      await notify(resolveHideLot(entity.id, selection.selected))
    }

    return shouldHide
  }

  async function highlightLot(tx: Transaction) {
    if (entity === null) return false

    if (tx.highlighted_by_auditor) {
      const shouldHighlight = await confirm(
        t("Désépingler le lot"),
        t("Voulez-vous retirer ce lot de la liste des lots mis de côté ?")
      )

      if (shouldHighlight) {
        await notify(resolveHighlightLots(entity.id, [tx.id]))
      }

      return Boolean(shouldHighlight)
    } else {
      const pinConfig = await prompt<PinConfig>((resolve) => (
        <PinPrompt
          role="auditor"
          title={t("Épingler ce lot")}
          description={t("Voulez-vous mettre ce lot de côté pour l'étudier plus tard ?")} // prettier-ignore
          onResolve={resolve}
        />
      ))

      if (pinConfig !== undefined) {
        const waiting = Promise.all([
          resolveHighlightLots(entity.id, [tx.id], pinConfig.checked),
          addAuditorComment(entity.id, [tx.id], pinConfig.comment, pinConfig.checked), // prettier-ignore
        ])

        await notify(waiting)
      }

      return Boolean(pinConfig)
    }
  }

  async function highlightLotSelection() {
    if (!entity) return false

    const pinConfig = await prompt<PinConfig>((resolve) => (
      <PinPrompt
        role="auditor"
        title={t("Épingler la sélection")}
        description={t("Voulez-vous mettre les lots sélectionnés de côté pour les étudier plus tard  ?")} // prettier-ignore
        onResolve={resolve}
      />
    ))

    if (pinConfig !== undefined) {
      const waiting = Promise.all([
        resolveHighlightLots(entity.id, selection.selected, pinConfig.checked),
        addAuditorComment(entity.id, selection.selected, pinConfig.comment, pinConfig.checked), // prettier-ignore
      ])

      await notify(waiting)
    }

    return Boolean(pinConfig)
  }

  return {
    loading: hideReq.loading || highlightReq.loading || commentReq.loading,
    hideLot,
    hideLotSelection,
    highlightLot,
    highlightLotSelection,
  }
}
