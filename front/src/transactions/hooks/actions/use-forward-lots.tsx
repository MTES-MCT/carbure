import { Transaction } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "common/hooks/use-api"

import { prompt } from "common/components/dialog"
import { useNotificationContext } from "common/components/notifications"
import { OperatorTransactionsToForwardPrompt } from "transactions/components/forward"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"

export interface LotForwarder {
  loading: boolean
  forwardSelection: (
    s: TransactionSelection,
    od?: EntityDeliverySite[]
  ) => Promise<void>
}

export default function useForwardLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  refresh: () => void
): LotForwarder {
  const notifications = useNotificationContext()

  const [request, resolveForward] = useAPI(api.forwardLots)

  async function notifyForward(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été transférés !"
          : "Le lot a bien été transféré !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible de transférer les lots."
          : "Impossible de transférer le lot.",
      })
    }
  }

  async function forwardSelection(
    s: TransactionSelection,
    outsourceddepots?: EntityDeliverySite[]
  ) {
    const txToTransfer = await prompt<Transaction[]>((resolve) => (
      <OperatorTransactionsToForwardPrompt
        selection={s}
        outsourceddepots={outsourceddepots}
        onResolve={resolve}
      />
    ))

    if (entity !== null && txToTransfer) {
      await notifyForward(
        resolveForward(
          entity.id,
          txToTransfer.map((t) => t.id)
        ),
        true
      )
    }
  }

  return {
    loading: request.loading,
    forwardSelection,
  }
}
