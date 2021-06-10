import { useTranslation } from "react-i18next"
import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { CommentPrompt } from "transactions/components/form-comments"
import {
  ValidationPrompt,
  ValidationSummaryPrompt,
} from "transactions/components/validation"
import { Transaction, TransactionQuery } from "common/types"

export interface LotValidator {
  loading: boolean
  validateLot: (tx: Transaction) => Promise<boolean>
  validateAndCommentLot: (tx: Transaction) => Promise<boolean>
  validateSelection: () => Promise<boolean>
  validateAll: () => Promise<boolean>
}

export default function useValidateLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void,
  stock?: boolean
): LotValidator {
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const [request, resolveValidate] = useAPI(api.validateLots)
  const [requestComment, resolveValidateAndComment] = useAPI(api.validateAndCommentLot) // prettier-ignore

  async function notifyValidate(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      if (res.valid > 0) {
        notifications.push({
          level: "success",
          text:
            res.submitted === 1
              ? t("Le lot a bien été envoyé !")
              : t("{{valid}} lots sur {{submitted}} ont bien été envoyés !", { res }), // prettier-ignore
        })
      }

      if (res.invalid > 0) {
        notifications.push({
          level: "error",
          text:
            res.submitted === 1
              ? t("Le lot n'a pas pu être validé !")
              : t("{{invalid}} lots sur {{submitted}} n'ont pas pu être validés !", { res }), // prettier-ignore
        })
      }

      if (res.duplicates > 0) {
        notifications.push({
          level: "warning",
          text:
            res.submitted === 1
              ? t("Un lot identique a été détecté dans la base de données !")
              : t("{{duplicates}} lots sont des doublons de lots existants !", { res }), // prettier-ignore
        })
      }
    } else {
      notifications.push({
        level: "error",
        text: t("Échec de la validation"),
      })
    }
  }

  async function validateLot(tx: Transaction) {
    const shouldValidate = await prompt<boolean>((resolve) => (
      <ValidationPrompt
        title={t("Envoyer lot")}
        description={t(
          "Vous vous apprêtez à envoyer ce lot à son destinataire, assurez-vous que les conditions ci-dessous sont respectées"
        )}
        onResolve={resolve}
      />
    ))

    if (entity !== null && shouldValidate) {
      await notifyValidate(resolveValidate(entity.id, [tx.id]))
    }

    return shouldValidate ?? false
  }

  async function validateAndCommentLot(tx: Transaction) {
    const comment = await prompt<string>((resolve) => (
      <CommentPrompt
        title={t("Envoyer lot")}
        description={t("Voulez vous renvoyer ce lot corrigé ?")}
        onResolve={resolve}
      />
    ))

    if (entity !== null && comment) {
      await notifyValidate(resolveValidateAndComment(entity.id, tx.id, comment))
    }

    return Boolean(comment)
  }

  async function validateSelection() {
    if (entity === null) return false

    const shouldValidate = await prompt<number[]>((resolve) => (
      <ValidationSummaryPrompt
        stock={stock}
        title={t("Envoyer la sélection")}
        description={t(
          "Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées"
        )}
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (shouldValidate) {
      await notifyValidate(resolveValidate(entity.id, selection.selected), true)
    }

    return Boolean(shouldValidate)
  }

  async function validateAll() {
    if (entity !== null) {
      const allTxids = await prompt<number[]>((resolve) => (
        <ValidationSummaryPrompt
          stock={stock}
          title={t("Envoyer tous ces brouillons")}
          description={t(
            "Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées"
          )}
          query={query}
          onResolve={resolve}
        />
      ))

      if (entity !== null && allTxids) {
        await notifyValidate(resolveValidate(entity.id, allTxids), true)
      }

      return Boolean(allTxids)
    }
    return false
  }

  return {
    loading: request.loading || requestComment.loading,
    validateLot,
    validateAndCommentLot,
    validateSelection,
    validateAll,
  }
}
