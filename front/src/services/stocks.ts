import { FilterSelection } from "../hooks/query/use-filters"
import { Lots, LotStatus, StockSnapshot, Transaction } from "./types"

import api from "./api"
import { toOption } from "./lots"

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
export function getStockStatus(transaction: Transaction): LotStatus {
  const status = transaction.lot.status.toLowerCase()
  const delivery = transaction.delivery_status

  if (status === "draft") {
    if (["A", "N"].includes(delivery)) {
      return LotStatus.ToSend
    }
  } else if (status === "validated") {
    if (["N"].includes(delivery)) {
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
  page: number,
  limit: number,
  query: string,
  sortBy: string,
  order: string
): Promise<Lots> {
  return api.get("/stocks", {
    ...filters,
    status,
    entity_id: entityID ?? null,
    from_idx: page * limit,
    sort_by: sortBy,
    limit,
    query,
    order,
  })
}

export function createDraftFromStock(
  entity_id: number,
  tx_id: number,
  volume: number,
  dae: string,
  delivery_date: string,
  client_id: string,
  delivery_site: string,
  delivery_site_country?: string
) {
  return api.post("/stocks/create-lot", {
    entity_id,
    tx_id,
    volume,
    dae,
    delivery_date,
    client: client_id,
    delivery_site,
    delivery_site_country,
  })
}

export function sendDraftsFromStock() {

}

export function sendAllDraftFromStock() {

}