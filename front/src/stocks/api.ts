import {
  ConvertETBE,
  Lots,
  LotStatus,
  StockDraft,
  Transaction,
  TransactionQuery,
  TransactionSummary,
  Snapshot,
} from "common/types"

import api from "common/services/api"
import {
  normalizeSummary,
  normalizeFilters,
  toOption,
} from "transactions/helpers"
import { EntitySelection } from "carbure/hooks/use-entity"

// extract the status name from the lot details
export function getStockStatus(
  tx: Transaction,
  entity: EntitySelection
): LotStatus {
  const status = tx.lot.status.toLowerCase()
  const delivery = tx.delivery_status

  const isAuthor = tx.lot.added_by?.id === entity?.id
  const isVendor = tx.carbure_vendor?.id === entity?.id
  const isClient = tx.carbure_client?.id === entity?.id

  if ((isVendor || isAuthor) && status === "draft") {
    if (["A", "N"].includes(delivery)) {
      return LotStatus.ToSend
    }
  } else if (isClient && status === "validated") {
    if (["N", "AC", "AA"].includes(delivery)) {
      return LotStatus.Inbox
    } else if (["A"].includes(delivery)) {
      return LotStatus.Stock
    }
  }

  return LotStatus.Weird
}

export function getStockSnapshot(entity_id: number): Promise<Snapshot> {
  return api.get("/stocks/snapshot", { entity_id }).then(normalizeFilters)
}

export function getStocks(query: TransactionQuery): Promise<Lots> {
  return api.get("/stocks", query)
}

export function getStocksSummary(
  query: TransactionQuery,
  selection: number[]
): Promise<TransactionSummary> {
  return api
    .get("/stocks/summary", { ...query, limit: null, page: 0, selection })
    .then(normalizeSummary)
}

export function downloadStocks(query: TransactionQuery) {
  return api.download("/stocks", {
    ...query,
    page: 0,
    limit: null,
    export: true,
  })
}

export function createDraftsFromStock(entity_id: number, drafts: StockDraft[]) {
  return api.post("/stocks/create-drafts", {
    entity_id,
    drafts: JSON.stringify(drafts),
  })
}

export function sendDraftsFromStock(
  entityID: number,
  transactionIDs: number[]
) {
  return api.post("/stocks/send-drafts", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function sendAllDraftFromStock(entityID: number) {
  return api.post("/stocks/send-all-drafts", {
    entity_id: entityID,
  })
}

export function convertToETBE(entityID: number, conversions: ConvertETBE[]) {
  return api.post("/stocks/convert-to-etbe", {
    entity_id: entityID,
    conversions: JSON.stringify(conversions),
  })
}

export function sendStockComplex(entityID: number) {
  return api.post("/stocks/send-complex", {
    entity_id: entityID,
  })
}

export function getDepots(
  entity_id: number,
  biocarburant_code: string
): Promise<string[]> {
  return api
    .get("/stocks/depots", { entity_id, biocarburant_code })
    .then((depots) => depots.map(toOption))
}

export function forwardLots(
  entityID: number,
  transactionIDs: number[],
  clientId: number | undefined,
  certificateID: string | undefined
) {
  return api.post("/stocks/forward", {
    entity_id: entityID,
    tx_ids: transactionIDs,
    recipient: clientId,
    certificate_id: certificateID,
  })
}
