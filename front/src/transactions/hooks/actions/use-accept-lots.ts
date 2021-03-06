import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { CommentWithTypePrompt } from "transactions/components/form-comments"

export interface LotAcceptor {
  loading: boolean
  acceptLot: (l: number) => Promise<boolean>
  acceptAndCommentLot: (l: number) => Promise<boolean>
  acceptSelection: () => Promise<boolean>
  acceptAllInbox: () => Promise<boolean>
}

export default function useAcceptLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): LotAcceptor {
  const notifications = useNotificationContext()

  const [request, resolveAccept] = useAPI(api.acceptLots)
  const [requestComment, resolveAcceptAndComment] = useAPI(api.acceptAndCommentLot) // prettier-ignore
  const [requestAll, resolveAcceptAll] = useAPI(api.acceptAllInboxLots)

  async function notifyAccept(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été acceptés !"
          : "Le lot a bien été accepté !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible d'accepter les lots."
          : "Impossible d'accepter le lot.",
      })
    }
  }

  async function acceptLot(lotID: number) {
    const shouldAccept = await confirm(
      "Accepter lot",
      "Voulez vous accepter ce lot ?"
    )

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAccept(entity.id, [lotID]))
    }

    return shouldAccept
  }

  async function acceptAndCommentLot(lotID: number) {
    const result = await prompt(
      "Accepter lot",
      "Voulez vous accepter ce lot sous réserve ?",
      CommentWithTypePrompt
    )

    if (entity !== null && result) {
      await notifyAccept(
        resolveAcceptAndComment(entity.id, lotID, result.comment, result.topic)
      )
    }

    return Boolean(result)
  }

  async function acceptSelection() {
    const shouldAccept = await confirm(
      "Accepter lot",
      "Voulez vous accepter les lots sélectionnés ?"
    )

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAccept(entity.id, selection.selected), true)
    }

    return shouldAccept
  }

  async function acceptAllInbox() {
    const shouldAccept = await confirm(
      "Accepter lot",
      "Voulez vous accepter tous ces lots ?"
    )

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAcceptAll(entity.id, year.selected), true)
    }

    return shouldAccept
  }

  return {
    loading: request.loading || requestAll.loading || requestComment.loading,
    acceptLot,
    acceptAndCommentLot,
    acceptSelection,
    acceptAllInbox,
  }
}
