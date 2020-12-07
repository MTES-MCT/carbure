import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "stocks/api"
import useAPI from "../../../common/hooks/use-api"
import { confirm } from "../../../common/components/dialog"
import { prompt } from "../../../common/components/dialog"
import { StockSendLotPrompt } from "stocks/components/stock-send-form"
import { useNotificationContext } from "../../../common/components/notifications"
import { TransactionSelection } from "../query/use-selection"

export interface LotSender {
  loading: boolean
  createDrafts: (i: number) => Promise<boolean>
  sendAllDrafts: () => Promise<boolean>
  sendSelection: () => Promise<boolean>
  sendLot: (l: number) => Promise<boolean>
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
      notifyCreated(
        resolveCreate(
          entity.id,
          txID,
          sent.volume,
          sent.dae,
          sent.delivery_date,
          sent.client_is_in_carbure
            ? `${sent.carbure_client?.name ?? ""}`
            : sent.unknown_client,
          sent.delivery_site_is_in_carbure
            ? sent.carbure_delivery_site?.depot_id ?? ""
            : sent.unknown_delivery_site,
          !sent.delivery_site_is_in_carbure
            ? sent.unknown_delivery_site_country?.code_pays ?? ""
            : ""
        )
      )
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

  return {
    loading:
      requestCreate.loading || requestSend.loading || requestSendAll.loading,
    createDrafts,
    sendSelection,
    sendAllDrafts,
    sendLot,
  }
}
