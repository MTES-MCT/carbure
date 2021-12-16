import {
  ConvertETBE,
  Lots,
  LotStatus,
  StockDraft,
  Transaction,
  TransactionQuery,
  TransactionSummary,
  Snapshot,
  Filters,
} from "common/types"

import api from "common/services/api"
import {
  normalizeSummary,
  normalizeSnapshot,
  toOption,
  normalizeFilter,
} from "transactions/helpers"
import { Entity } from "carbure/types"
import { TFunction } from "react-i18next"
import { Option } from "common/components/select"

// extract the status name from the lot details
export function getStockStatus(tx: Transaction, entity: Entity): LotStatus {
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
    } else if (["A", "F"].includes(delivery)) {
      return LotStatus.Stock
    }
  }

  return LotStatus.Weird
}

export function getStockSnapshot(
  entity_id: number,
  t: TFunction
): Promise<Snapshot> {
  return api
    .get("/stocks/snapshot", { entity_id })
    .then((s) => normalizeSnapshot(s, t))
}

export function getStocks(query: TransactionQuery): Promise<Lots> {
  return api.get("/stocks", query)
}

export function getStocksSummary(
  query: TransactionQuery,
  selection: number[]
): Promise<TransactionSummary> {
  return api
    .get("/stocks/summary", {
      ...query,
      limit: null,
      from_idx: 0,
      selection,
      year: null,
    })
    .then(normalizeSummary)
}

export function getStockFilters(
  field: Filters,
  params: TransactionQuery,
  t: TFunction
): Promise<Option[]> {
  return api
    .get("/stocks/filters", {
      field,
      ...params,
      limit: null,
      from_idx: 0,
      year: null,
    })
    .then((filter) => normalizeFilter(field, filter, t))
}

export function downloadStocks(query: TransactionQuery) {
  return api.download("/stocks", {
    ...query,
    from_idx: 0,
    limit: null,
    year: null,
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
