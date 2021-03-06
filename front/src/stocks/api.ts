import { FilterSelection } from "transactions/hooks/query/use-filters"
import {
  ConvertETBE,
  Lots,
  LotStatus,
  StockDraft,
  StockSnapshot,
  Transaction,
} from "common/types"

import api from "common/services/api"
import { toOption } from "transactions/helpers"
import { EntitySelection } from "carbure/hooks/use-entity"
import { StatusSelection } from "transactions/hooks/query/use-status"

// give the same type to all filters in order to render them easily
function normalizeStockSnapshotFilters(snapshot: any): StockSnapshot {
  snapshot.filters = {
    matieres_premieres: snapshot.filters.matieres_premieres,
    biocarburants: snapshot.filters.biocarburants,
    countries_of_origin: snapshot.filters.countries_of_origin,
    production_sites: snapshot.filters.production_sites.map(toOption),
    delivery_sites: snapshot.filters.delivery_sites.map(toOption),
  }
  return snapshot
}

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

export function getStockSnapshot(entity_id: number): Promise<StockSnapshot> {
  return api
    .get("/stocks/snapshot", { entity_id })
    .then(normalizeStockSnapshotFilters)
}

export function getStocks(
  entityID: number | undefined,
  filters: FilterSelection["selected"],
  status: string,
  page: number = 0,
  limit: number | null = null,
  query: string = "",
  sortBy: string = "",
  order: string = ""
): Promise<Lots> {
  return api.get("/stocks", {
    ...filters,
    status,
    entity_id: entityID ?? null,
    from_idx: page * (limit ?? 1),
    sort_by: sortBy,
    limit,
    query,
    order,
  })
}

export function downloadStocks(
  status: LotStatus,
  entityID: number | undefined,
  filters: FilterSelection["selected"],
  query: string,
  sortBy: string,
  order: string
) {
  return api.download("/stocks", {
    ...filters,
    status,
    entity_id: entityID ?? null,
    sort_by: sortBy,
    query,
    order,
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
