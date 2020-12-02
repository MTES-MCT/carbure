import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/stocks"
import useAPI from "../helpers/use-api"

import { prompt } from "../../components/system/dialog"
import { StockSendLotPrompt } from "../../components/stock/stock-send-form"
import { useNotificationContext } from "../../components/system/notifications"
import { TransactionSelection } from "../query/use-selection"

export interface LotSender {
  loading: boolean
  sendLot: (i: number) => Promise<boolean>
  sendAll: () => Promise<boolean>
  sendSelection: () => Promise<boolean>
}

export default function useSendLot(
  entity: EntitySelection,
  selection: TransactionSelection,
  refresh: () => void
): LotSender {
  const notifications = useNotificationContext()
  const [request, resolveSend] = useAPI(api.createDraftFromStock)
  const [requestAll, resolveSendAll] = useAPI(api.sendDraftsFromStock)
  const [requestAll, resolveSendAll] = useAPI(api.sendAllDraftFromStock)

  async function sendLot(txID: number) {
    const sent = await prompt(
      "Préparer lot",
      "Veuillez préciser les détails du lot à envoyer",
      StockSendLotPrompt
    )

    if (entity !== null && sent) {
      const res = await resolveSend(
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

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le lot a bien été préparé pour l'envoi !",
        })
      } else {
        notifications.push({
          level: "success",
          text: "Impossible d'envoyer le lot.",
        })
      }
    }

    return sent
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

    if (entity !== null && shouldDelete) {
      notifySend(resolveSendAll(entity.id), true)
    }

    return shouldSend
  }

  return { loading: request.loading, sendLot, sendSelection, sendAllDrafts }
}
