import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"

export interface LotForwarder {
  loading: boolean
  forwardSelection: (l: EntitySelection) => Promise<boolean>
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

  async function forwardSelection() {
    const shouldAccept = await confirm(
      "Transférer lot",
      "Voulez vous transférer les lots sélectionnés ?"
    )

    if (entity !== null && shouldAccept) {
      await notifyForward(resolveForward(entity.id, selection.selected), true)
    }

    return shouldAccept
  }

  return {
    loading: request.loading,
    forwardSelection,
  }
}
