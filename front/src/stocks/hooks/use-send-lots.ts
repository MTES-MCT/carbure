import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "stocks/api"
import useAPI from "common/hooks/use-api"
import { confirm } from "common/components/dialog"
import { prompt } from "common/components/dialog"
import { StockSendLotPrompt } from "stocks/components/send-form"
import {
  ConvertETBEComplexPromptFactory,
  ConvertETBEPrompt,
} from "stocks/components/convert-etbe-form"
import { useNotificationContext } from "common/components/notifications"
import { TransactionSelection } from "transactions/hooks/query/use-selection"
import { StockDraft } from "common/types"

export interface LotSender {
  loading: boolean
  createDrafts: (i: number) => Promise<boolean>
  sendAllDrafts: () => Promise<boolean>
  sendSelection: () => Promise<boolean>
  sendLot: (l: number) => Promise<boolean>
  convertETBE: (l: number) => Promise<boolean>
  convertETBEComplex: () => Promise<boolean>
}

export default function useSendLot(
  entity: EntitySelection,
  selection: TransactionSelection,
  refresh: () => void
): LotSender {
  const notifications = useNotificationContext()
  const [requestCreate, resolveCreate] = useAPI(api.createDraftsFromStock)
  const [requestSend, resolveSend] = useAPI(api.sendDraftsFromStock)
  const [requestSendAll, resolveSendAll] = useAPI(api.sendAllDraftFromStock)
  const [requestETBE, resolveETBE] = useAPI(api.convertToETBE)

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
    const sent = await prompt(
      "Préparer lot",
      "Veuillez préciser les détails du lot à envoyer",
      StockSendLotPrompt
    )

    if (entity !== null && sent) {
      const draft: StockDraft = {
        tx_id: txID,
        volume: sent.volume,
        dae: sent.dae,
        delivery_date: sent.delivery_date,
        client: sent.client_is_in_carbure
          ? `${sent.carbure_client?.name ?? ""}`
          : sent.unknown_client,
        delivery_site: sent.delivery_site_is_in_carbure
          ? sent.carbure_delivery_site?.depot_id ?? ""
          : sent.unknown_delivery_site,
        delivery_site_country: !sent.delivery_site_is_in_carbure
          ? sent.unknown_delivery_site_country?.code_pays ?? ""
          : "",
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
    const shouldSend = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer les lots sélectionnés ?"
    )

    if (entity !== null && shouldSend) {
      notifySend(resolveSend(entity.id, selection.selected), true)
    }

    return shouldSend
  }

  async function sendAllDrafts() {
    const shouldSend = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer tous ces lots ?"
    )

    if (entity !== null && shouldSend) {
      notifySend(resolveSendAll(entity.id), true)
    }

    return shouldSend
  }

  async function convertETBE(txID: number) {
    const sent = await prompt(
      "Conversion ETBE",
      "Veuillez préciser les détails du lot transformé",
      ConvertETBEPrompt
    )

    if (entity !== null && sent) {
      sent.previous_stock_tx_id = txID
      notifyCreated(resolveETBE(entity.id, [sent]))
    }

    return Boolean(sent)
  }

  async function convertETBEComplex() {
    if (entity === null) return false

    const conversions = await prompt(
      "Conversion ETBE",
      "",
      ConvertETBEComplexPromptFactory(entity.id)
    )

    if (conversions) {
      notifyCreated(resolveETBE(entity.id, conversions))
    }

    return Boolean(conversions)
  }

  return {
    loading:
      requestCreate.loading ||
      requestSend.loading ||
      requestSendAll.loading ||
      requestETBE.loading,
    createDrafts,
    sendSelection,
    sendAllDrafts,
    sendLot,
    convertETBE,
    convertETBEComplex,
  }
}
