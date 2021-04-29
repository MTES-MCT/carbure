import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "stocks/api"

import useAPI from "common/hooks/use-api"
import { confirm } from "common/components/dialog"
import { prompt } from "common/components/dialog"
import {
  StockSendDetails,
  StockSendLotPrompt,
} from "stocks/components/send-form"
import { ConvertETBEComplexPrompt } from "stocks/components/convert-etbe-form"

import {
  ForwardClientFormState,
  ForwardLotsClientSelectionPrompt,
} from "stocks/components/forward-lots-form"
import { useNotificationContext } from "common/components/notifications"
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { ConvertETBE, StockDraft, TransactionQuery } from "common/types"
import { isKnown } from "transactions/components/form/fields"
import { SummaryPrompt } from "transactions/components/summary"

export interface LotSender {
  loading: boolean
  createDrafts: (i: number) => Promise<boolean>
  sendAllDrafts: () => Promise<boolean>
  sendSelection: () => Promise<boolean>
  sendLot: (l: number) => Promise<boolean>
  // convertETBE: (l: number) => Promise<boolean>
  convertETBEComplex: () => Promise<boolean>
  forwardLots: () => Promise<boolean>
}

export default function useSendLot(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void
): LotSender {
  const notifications = useNotificationContext()
  const [requestCreate, resolveCreate] = useAPI(api.createDraftsFromStock)
  const [requestSend, resolveSend] = useAPI(api.sendDraftsFromStock)
  const [requestETBE, resolveETBE] = useAPI(api.convertToETBE)
  const [requestForward, resolveForward] = useAPI(api.forwardLots)

  async function notifyCreated(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été créés !"
          : "Le lot a bien été créé !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible de créer les lots."
          : "Impossible de créer le lot.",
      })
    }
  }

  async function notifySend(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: many
          ? "Les lots ont bien été envoyés !"
          : "Le lot a bien été envoyé !",
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? "Impossible d'envoyer les lots."
          : "Impossible d'envoyer le lot.",
      })
    }
  }

  async function createDrafts(txID: number) {
    const sent = await prompt<StockSendDetails>((resolve) => (
      <StockSendLotPrompt entity={entity} onResolve={resolve} />
    ))

    if (entity !== null && sent) {
      const draft: StockDraft = {
        tx_id: txID,
        volume: sent.volume,
        dae: sent.dae,
        delivery_date: sent.delivery_date,
        mac: sent.mac,
        client: isKnown(sent.client) ? sent.client.name : sent.client ?? "",
        delivery_site: isKnown(sent.delivery_site)
          ? sent.delivery_site.depot_id
          : sent.delivery_site ?? "",
        delivery_site_country: sent.delivery_site_country?.code_pays,
      }

      notifyCreated(resolveCreate(entity.id, [draft]))
    }

    return Boolean(sent)
  }

  async function sendLot(lotID: number) {
    const shouldSend = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer ce lot ?"
    )

    if (entity !== null && shouldSend) {
      notifySend(resolveSend(entity.id, [lotID]), true)
    }

    return shouldSend
  }

  async function sendSelection() {
    if (entity === null) return false

    const shouldSend = await prompt<number[]>((resolve) => (
      <SummaryPrompt
        stock
        title="Envoyer la sélection"
        description="Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées :"
        query={query}
        onResolve={resolve}
      />
    ))

    if (shouldSend) {
      notifySend(resolveSend(entity.id, selection.selected), true)
    }

    return Boolean(shouldSend)
  }

  async function sendAllDrafts() {
    if (entity !== null) {
      const allTxids = await prompt<number[]>((resolve) => (
        <SummaryPrompt
          stock
          title="Envoyer tous ces lots"
          description="Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées :"
          query={query}
          onResolve={resolve}
        />
      ))

      if (entity !== null && allTxids) {
        await notifySend(resolveSend(entity.id, allTxids), true)
      }
      return Boolean(allTxids)
    }
    return false
  }

  // async function convertETBE(txID: number) {
  //   const sent = await prompt(
  //     "Conversion ETBE",
  //     "Veuillez préciser les détails du lot transformé",
  //     ConvertETBEPrompt
  //   )

  //   if (entity !== null && sent) {
  //     sent.previous_stock_tx_id = txID
  //     notifyCreated(resolveETBE(entity.id, [sent]))
  //   }

  //   return Boolean(sent)
  // }

  async function convertETBEComplex() {
    if (entity === null) return false

    const conversions = await prompt<ConvertETBE[]>((resolve) => (
      <ConvertETBEComplexPrompt entityID={entity.id} onResolve={resolve} />
    ))

    if (conversions) {
      notifyCreated(resolveETBE(entity.id, conversions))
    }

    return Boolean(conversions)
  }

  async function forwardLots() {
    if (entity === null) return false

    const data = await prompt<ForwardClientFormState>((resolve) => (
      <ForwardLotsClientSelectionPrompt
        entityID={entity.id}
        onResolve={resolve}
      />
    ))

    if (data) {
      notifyCreated(
        resolveForward(
          entity.id,
          selection.selected,
          data?.carbure_client?.id,
          data?.certificate ?? ""
        )
      )
    }

    return Boolean(data)
  }

  return {
    loading:
      requestCreate.loading ||
      requestSend.loading ||
      requestETBE.loading ||
      requestForward.loading,
    createDrafts,
    sendSelection,
    sendLot,
    sendAllDrafts,
    // convertETBE,
    convertETBEComplex,
    forwardLots,
  }
}
