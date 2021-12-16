import { useTranslation } from "react-i18next"
import { Entity } from "carbure/types"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { Transaction, TransactionQuery } from "common/types"
import { SummaryPrompt } from "transactions/components/summary"

export interface LotDeleter {
  loading: boolean
  deleteLot: (tx: Transaction) => Promise<boolean>
  deleteSelection: () => Promise<boolean>
  deleteAll: () => Promise<boolean>
}

export default function useDeleteLots(
  entity: Entity,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void,
  stock?: boolean
): LotDeleter {
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const [request, resolveDelete] = useAPI(api.deleteLots)

  async function notifyDelete(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? t("Les lots ont bien été supprimés !")
          : t("Le lot a bien été supprimé !"),
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? t("Impossible de supprimer les lots.")
          : t("Impossible de supprimer le lot."),
      })
    }
  }

  async function deleteLot(tx: Transaction) {
    const shouldDelete = await confirm(
      t("Supprimer lot"),
      t("Voulez vous supprimer ce lot ?")
    )

    if (entity !== null && shouldDelete) {
      await notifyDelete(resolveDelete(entity.id, [tx.id]))
    }

    return shouldDelete
  }

  async function deleteSelection() {
    const shouldDelete = await prompt<number[]>((resolve) => (
      <SummaryPrompt
        stock={stock}
        title={t("Supprimer lot")}
        description={t("Voulez vous supprimer les lots sélectionnés ?")}
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (entity !== null && shouldDelete) {
      await notifyDelete(resolveDelete(entity.id, selection.selected), true)
    }

    return Boolean(shouldDelete)
  }

  async function deleteAll() {
    if (entity !== null) {
      const allTxids = await prompt<number[]>((resolve) => (
        <SummaryPrompt
          stock={stock}
          title={t("Supprimer tous ces brouillons")}
          description={t("Voulez vous supprimer tous ces lots ?")}
          query={query}
          selection={selection.selected}
          onResolve={resolve}
        />
      ))

      if (entity !== null && allTxids) {
        await notifyDelete(resolveDelete(entity.id, allTxids), true)
      }

      return Boolean(allTxids)
    }

    return false
  }

  return {
    loading: request.loading,
    deleteLot,
    deleteSelection,
    deleteAll,
  }
}
