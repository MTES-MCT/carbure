import { ApiFilters, Lot, Lots, LotStatus, Snapshot } from "./types"

import api from "./api"
import { FilterSelection } from "../hooks/use-transactions"
import { TransactionFormState } from "../hooks/use-transaction-details"

// give the same type to all filters in order to render them easily
function normalizeFilters(filters: ApiFilters): Snapshot["filters"] {
  return {
    matieres_premieres: filters.matieres_premieres,
    biocarburants: filters.biocarburants,
    countries_of_origin: filters.countries_of_origin,
    periods: filters.periods.map((filter: string) => ({
      value: filter,
      label: filter,
    })),
    production_sites: filters.production_sites.map((filter: string) => ({
      value: filter,
      label: filter,
    })),
    clients: filters.clients.map((filter: string) => ({
      value: filter,
      label: filter,
    })),
  }
}

// extract the status name from the lot details
export function getStatus(lot: Lot): LotStatus {
  const status = lot.lot.status.toLowerCase()
  const delivery = lot.delivery_status

  if (status === "draft") {
    return LotStatus.Draft
  } else if (status === "validated") {
    if (["N", "AA"].includes(delivery)) {
      return LotStatus.Validated
    } else if (delivery === "AC") {
      return LotStatus.ToFix
    } else if (delivery === "A") {
      return LotStatus.Accepted
    }
  }

  return LotStatus.Weird
}

export async function getSnapshot(producerID: number): Promise<Snapshot> {
  const snapshot = await api.get("/lots/snapshot", {
    producer_id: producerID,
  })

  snapshot.filters = normalizeFilters(snapshot.filters)

  return snapshot
}

export function getLots(
  status: LotStatus,
  producerID: number,
  filters: FilterSelection["selected"],
  pagination: { page: number; limit: number }
): Promise<Lots> {
  return api.get("/lots", {
    status,
    producer_id: producerID,
    ...filters,
    from_idx: pagination.page * pagination.limit,
    limit: pagination.limit,
  })
}

export function addLots(
  entityID: number,
  lotDetails: TransactionFormState
): Promise<void> {
  return api.post("/lots/add", { entity_id: entityID, ...lotDetails })
}
