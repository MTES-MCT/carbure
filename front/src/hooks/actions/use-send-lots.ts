import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/lots"
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
    const shouldSend = await prompt(
      "Envoyer lot",
      "Voulez vous envoyer ce lot ?",
      StockSendLotPrompt
    )

    if (entity !== null && shouldSend) {
      await resolveSend(entity.id, txID, shouldSend.volume, shouldSend.client, shouldSend.delivery_site, shouldSend.delivery_date).then(refresh)
    }

    return shouldSend
  }

  return { loading: request.loading, sendLot }
}
