import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/stocks"
import useAPI from "../helpers/use-api"

import { prompt } from "../../components/system/dialog"
import { StockSendLotPrompt } from "../../components/stock/stock-send-form"

export interface LotSender {
  loading: boolean
  sendLot: (i: number) => Promise<any>
}

export default function useSendLot(
  entity: EntitySelection,
  refresh: () => void
): LotSender {
  const [request, resolveSend] = useAPI(api.sendLotFromStock)

  async function sendLot(txID: number) {
    const sent = await prompt(
      "Envoyer lot",
      "Veuillez préciser les détails du lot à envoyer",
      StockSendLotPrompt
    )

    if (entity !== null && sent) {
      await resolveSend(
        entity.id,
        txID,
        sent.volume,
        sent.dae,
        sent.delivery_date,
        sent.client_is_in_carbure
          ? `${sent.carbure_client?.id ?? ""}`
          : sent.unknown_client,
        sent.delivery_site_is_in_carbure
          ? sent.carbure_delivery_site?.name ?? ""
          : sent.unknown_delivery_site,
        !sent.delivery_site_is_in_carbure
          ? sent.unknown_delivery_site_country?.code_pays ?? ""
          : ""
      ).then(refresh)
    }

    return sent
  }

  return { loading: request.loading, sendLot }
}
