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
import { ConvertETBE, StockDraft } from "common/types"
import { ValidationPrompt } from "transactions/components/validation"
import { YearSelection } from "transactions/hooks/query/use-year"
import { FilterSelection } from "transactions/hooks/query/use-filters"
import { SearchSelection } from "transactions/hooks/query/use-search"
import { SpecialSelection } from "transactions/hooks/query/use-special"

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
  filters: FilterSelection,
  search: SearchSelection,
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
      <StockSendLotPrompt onResolve={resolve} />
    ))

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
    if (entity === null) return false

    const shouldSend = await prompt<boolean>((resolve) => (
      <ValidationPrompt
        stock
        title="Envoyer la sélection"
        description="Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées :"
        entityID={entity.id}
        selection={selection.selected}
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
      const filteredDrafts = await api.getStocks(entity.id, filters["selected"], "tosend", 0, null, search.query)
      const nbClients = new Set(
        filteredDrafts.lots.map((o) => o.carbure_client ? o.carbure_client.name : o.unknown_client)
      ).size
      const totalVolume = filteredDrafts.lots
        .map((o) => o.lot.volume)
        .reduce((sum, vol) => sum + vol)
      const clientsStr = nbClients > 1 ? "clients" : "client"
      const allTxids = filteredDrafts.lots.map((o) => o.id)

      const shouldSend = await prompt<boolean>((resolve) => (
        <ValidationPrompt
          stock
          title="Envoyer tous ces brouillons"
          description={`Voulez êtes sur le point d'envoyer ${filteredDrafts.lots.length} lots à ${nbClients} ${clientsStr} pour un total de ${totalVolume} litres ?`}
          entityID={entity.id}
          selection={allTxids}
          onResolve={resolve}
        />
      ))

      if (entity !== null && shouldSend) {
        await notifySend(resolveSend(entity.id, allTxids), true)
      }
      return Boolean(shouldSend)
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
