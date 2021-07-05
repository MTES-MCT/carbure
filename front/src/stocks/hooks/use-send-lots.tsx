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
import {
  ConvertETBE,
  StockDraft,
  Transaction,
  TransactionQuery,
} from "common/types"
import { isKnown } from "transactions/components/form/fields"
import { SummaryPrompt } from "transactions/components/summary"
import { useTranslation } from "react-i18next"

export interface LotSender {
  loading: boolean
  createDrafts: (tx: Transaction) => Promise<boolean>
  sendAllDrafts: () => Promise<boolean>
  sendSelection: () => Promise<boolean>
  sendLot: (tx: Transaction) => Promise<boolean>
  convertETBEComplex: () => Promise<boolean>
  forwardLots: () => Promise<boolean>
}

export default function useSendLot(
  entity: EntitySelection,
  selection: TransactionSelection,
  query: TransactionQuery,
  refresh: () => void
): LotSender {
  const { t } = useTranslation()
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
          ? t("Les lots ont bien été créés !")
          : t("Le lot a bien été créé !"),
      })
    } else {
      notifications.push({
        level: "error",
        text: many
          ? t("Impossible de créer les lots.")
          : t("Impossible de créer le lot."),
      })
    }
  }

  async function notifySend(promise: Promise<any>, many: boolean = false) {
    const res = await promise

    if (res) {
      refresh()

      if (res.valid > 0) {
        notifications.push({
          level: "success",
          text:
            res.total === 1
              ? t("Le lot a bien été envoyé !")
              : t("{{valid}} lots sur {{total}} ont bien été envoyés !", res),
        })
      }

      if (res.invalid > 0) {
        notifications.push({
          level: "error",
          list: res.errors,
          text:
            res.total === 1
              ? t("Le lot n'a pas pu être validé !")
              : t("{{invalid}} lots sur {{total}} n'ont pas pu être validés !", res), // prettier-ignore
        })
      }

      if (res.duplicates > 0) {
        notifications.push({
          level: "warning",
          text:
            res.total === 1
              ? t("Un lot identique a été détecté dans la base de données !")
              : t("{{duplicates}} lots sont des doublons de lots existants !", res), // prettier-ignore
        })
      }
    } else {
      notifications.push({
        level: "error",
        text: t("Échec de la validation"),
      })
    }
  }

  async function createDrafts(tx: Transaction) {
    const sent = await prompt<StockSendDetails>((resolve) => (
      <StockSendLotPrompt entity={entity} onResolve={resolve} />
    ))

    if (entity !== null && sent) {
      const draft: StockDraft = {
        tx_id: tx.id,
        volume: sent.volume,
        dae: sent.dae,
        delivery_date: sent.delivery_date,
        mac: sent.mac,
        client: isKnown(sent.client) ? sent.client.name : sent.client ?? "",
        delivery_site: isKnown(sent.delivery_site)
          ? sent.delivery_site.depot_id
          : sent.delivery_site ?? "",
        delivery_site_country: sent.delivery_site_country?.code_pays,
        vendor_certificate: sent.carbure_vendor_certificate,
      }

      await notifyCreated(resolveCreate(entity.id, [draft]))
    }

    return Boolean(sent)
  }

  async function sendLot(tx: Transaction) {
    const shouldSend = await confirm(
      t("Envoyer lots"),
      t("Voulez vous envoyer ce lot ?")
    )

    if (entity !== null && shouldSend) {
      await notifySend(resolveSend(entity.id, [tx.id]), true)
    }

    return shouldSend
  }

  async function sendSelection() {
    if (entity === null) return false

    const shouldSend = await prompt<number[]>((resolve) => (
      <SummaryPrompt
        stock
        title={t("Envoyer la sélection")}
        description={t("Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées")} // prettier-ignore
        query={query}
        selection={selection.selected}
        onResolve={resolve}
      />
    ))

    if (shouldSend) {
      await notifySend(resolveSend(entity.id, selection.selected), true)
    }

    return Boolean(shouldSend)
  }

  async function sendAllDrafts() {
    if (entity !== null) {
      const allTxids = await prompt<number[]>((resolve) => (
        <SummaryPrompt
          stock
          title={t("Envoyer tous ces lots")}
          description={t("Vous vous apprêtez à envoyer ces lots à leur destinataire, assurez-vous que les conditions ci-dessous sont respectées")} // prettier-ignore
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

  async function convertETBEComplex() {
    if (entity === null) return false

    const conversions = await prompt<ConvertETBE[]>((resolve) => (
      <ConvertETBEComplexPrompt entityID={entity.id} onResolve={resolve} />
    ))

    if (conversions) {
      await notifyCreated(resolveETBE(entity.id, conversions))
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
      await notifyCreated(
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
    convertETBEComplex,
    forwardLots,
  }
}
