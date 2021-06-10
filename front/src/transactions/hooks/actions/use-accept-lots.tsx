import { useTranslation } from "react-i18next"
import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm, prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import {
  CommentPrompt,
  CommentWithTypePrompt,
  CommentWithType,
} from "transactions/components/form-comments"
import { Transaction, TransactionQuery } from "common/types"
import { SummaryPrompt } from "transactions/components/summary"

export interface LotAcceptor {
  loading: boolean
  acceptLot: (tx: Transaction) => Promise<boolean>
  acceptAndCommentLot: (tx: Transaction) => Promise<boolean>
  acceptSelection: () => Promise<boolean>
  acceptAllInbox: () => Promise<boolean>
  amendLot: (tx: Transaction) => Promise<boolean>
  askForCorrection: (tx: Transaction) => Promise<boolean>
}

export default function useAcceptLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void,
  stock?: boolean
): LotAcceptor {
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const [request, resolveAccept] = useAPI(api.acceptLots)
  const [requestAmend, resolveAmendLot] = useAPI(api.amendAndCommentLot)
  const [requestComment, resolveAcceptAndComment] = useAPI(api.acceptAndCommentLot) // prettier-ignore

  async function notifyAccept(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? t("Les lots ont bien été acceptés !")
          : t("Le lot a bien été accepté !"),
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? t("Impossible d'accepter les lots.")
          : t("Impossible d'accepter le lot."),
      })
    }
  }

  async function notifyCorrection(promise: Promise<any>) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: t("Le lot a bien été envoyé en correction !"),
      })
    } else {
      notifications.push({
        level: "error",
        text: t("Impossible de corriger ce lot."),
      })
    }
  }

  async function acceptLot(tx: Transaction) {
    const shouldAccept = await confirm(
      t("Accepter lot"),
      t("Voulez vous accepter ce lot ?")
    )

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAccept(entity.id, [tx.id]))
    }

    return shouldAccept
  }

  async function acceptAndCommentLot(tx: Transaction) {
    const result = await prompt<CommentWithType>((resolve) => (
      <CommentWithTypePrompt onResolve={resolve} />
    ))

    if (entity !== null && result) {
      await notifyAccept(
        resolveAcceptAndComment(entity.id, tx.id, result.comment, result.topic)
      )
    }

    return Boolean(result)
  }

  async function askForCorrection(tx: Transaction) {
    const result = await prompt<CommentWithType>((resolve) => (
      <CommentWithTypePrompt
        title={t("Demander une correction")}
        description={t(
          "Voulez-vous renvoyer ce lot à son fournisseur pour correction ?"
        )}
        onResolve={resolve}
      />
    ))

    if (entity !== null && result) {
      await notifyCorrection(
        resolveAcceptAndComment(entity.id, tx.id, result.comment, result.topic)
      )
    }

    return Boolean(result)
  }

  async function amendLot(tx: Transaction) {
    const comment = await prompt<string>((resolve) => (
      <CommentPrompt
        title={t("Corriger le lot")}
        description={t(
          "Voulez-vous modifier ce lot accepté ? Si la déclaration pour cette période a déjà été validée, il vous faudra la soumettre à nouveau une fois la correction acceptée par votre client."
        )}
        onResolve={resolve}
      />
    ))

    if (entity !== null && comment) {
      await notifyCorrection(resolveAmendLot(entity.id, tx.id, comment))
    }

    return Boolean(comment)
  }

  async function acceptSelection() {
    const shouldAccept = await prompt<number[]>((resolve) => (
      <SummaryPrompt
        stock={stock}
        title={t("Accepter lot")}
        description={t("Voulez vous accepter les lots sélectionnés ?")}
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (entity !== null && shouldAccept) {
      await notifyAccept(resolveAccept(entity.id, selection.selected), true)
    }

    return Boolean(shouldAccept)
  }

  async function acceptAllInbox() {
    if (entity !== null) {
      const allTxids = await prompt<number[]>((resolve) => (
        <SummaryPrompt
          stock={stock}
          title={t("Accepter tout")}
          description={t("Voulez vous accepter tous ces lots ?")}
          query={query}
          selection={selection.selected}
          onResolve={resolve}
        />
      ))

      if (entity !== null && allTxids) {
        await notifyAccept(resolveAccept(entity.id, allTxids), true)
      }

      return Boolean(allTxids)
    }

    return false
  }

  return {
    loading: request.loading || requestComment.loading || requestAmend.loading,
    acceptLot,
    acceptAndCommentLot,
    acceptSelection,
    acceptAllInbox,
    amendLot,
    askForCorrection,
  }
}
