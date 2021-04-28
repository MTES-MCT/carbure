import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { prompt } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { CommentPrompt } from "transactions/components/form-comments"
import { ValidationPrompt } from "transactions/components/validation"
import { LotStatus, TransactionQuery } from "common/types"

export interface LotValidator {
  loading: boolean
  validateLot: (l: number) => Promise<boolean>
  validateAndCommentLot: (l: number) => Promise<boolean>
  validateSelection: () => Promise<boolean>
  validateAll: () => Promise<boolean>
}

export default function useValidateLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  filters: TransactionQuery,
  refresh: () => void
): LotValidator {
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
              ? "Le lot a bien été envoyé !"
              : `${res.valid} lots sur ${res.submitted} ont bien été envoyés !`,
        })
      }

      if (res.invalid > 0) {
        notifications.push({
          level: "error",
          text:
            res.submitted === 1
              ? "Le lot n'a pas pu être validé !"
              : `${res.invalid} lots sur ${res.submitted} n'ont pas pu être validés !`,
        })
      }

      if (res.duplicates > 0) {
        notifications.push({
          level: "warning",
          text:
            res.submitted === 1
              ? "Un lot identique a été détecté dans la base de données !"
              : `${res.duplicates} lots sont des doublons de lots existants !`,
        })
      }
    } else {
      notifications.push({
        level: "error",
        text: "Échec de la validation",
      })
    }
  }

  async function validateLot(lotID: number) {
    const shouldValidate = await prompt<boolean>((resolve) => (
      <ValidationPrompt
        title="Envoyer lot"
        description="Vous vous apprêtez à envoyer ce lot à son destinataire, assurez-vous que les conditions ci-dessous sont respectées :"
        onResolve={resolve}
      />
    ))

    if (entity !== null && shouldValidate) {
      await notifyValidate(resolveValidate(entity.id, [lotID]))
    }

    return shouldValidate ?? false
  }

  async function validateAndCommentLot(lotID: number) {
    const comment = await prompt<string>((resolve) => (
      <CommentPrompt
        title="Envoyer lot"
        description="Voulez vous renvoyer ce lot corrigé ?"
        onResolve={resolve}
      />
    ))

    if (entity !== null && comment) {
      await notifyValidate(resolveValidateAndComment(entity.id, lotID, comment))
    }

    return Boolean(comment)
  }

  async function validateSelection() {
    if (entity === null) return false

    const shouldValidate = await prompt<boolean>((resolve) => (
      <ValidationPrompt
        title="Envoyer la sélection"
        description="Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées :"
        entityID={entity.id}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (shouldValidate) {
      await notifyValidate(resolveValidate(entity.id, selection.selected), true)
    }

    return shouldValidate ?? false
  }

  async function validateAll() {
    if (entity !== null) {
      const filteredDrafts = await api.getLots(filters)
      const nbClients = new Set(
        filteredDrafts.lots.map((o) =>
          o.carbure_client ? o.carbure_client.name : o.unknown_client
        )
      ).size
      const totalVolume = filteredDrafts.lots
        .map((o) => o.lot.volume)
        .reduce((sum, vol) => sum + vol)
      const clientsStr = nbClients > 1 ? "clients" : "client"
      const allTxids = filteredDrafts.lots.map((o) => o.id)

      const shouldValidate = await prompt<boolean>((resolve) => (
        <ValidationPrompt
          stock
          title="Envoyer tous ces brouillons"
          description={`Voulez êtes sur le point d'envoyer ${filteredDrafts.lots.length} lots à ${nbClients} ${clientsStr} pour un total de ${totalVolume} litres ?`}
          filters={filters}
          onResolve={resolve}
        />
      ))

      if (entity !== null && shouldValidate) {
        await notifyValidate(resolveValidate(entity.id, allTxids), true)
      }
      return Boolean(shouldValidate)
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
