import { Lot, Lots, LotStatus, Snapshot } from "./types"

import api from "./api"
import { FilterSelection } from "../hooks/use-transactions"
import { TransactionFormState } from "../hooks/use-transaction-details"

function toOption(value: string) {
  return { value, label: value }
}

// give the same type to all filters in order to render them easily
function normalizeFilters(snapshot: any): Snapshot {
  snapshot.filters = {
    matieres_premieres: snapshot.filters.matieres_premieres,
    biocarburants: snapshot.filters.biocarburants,
    countries_of_origin: snapshot.filters.countries_of_origin,
    periods: snapshot.filters.periods.map(toOption),
    production_sites: snapshot.filters.production_sites.map(toOption),
    clients: snapshot.filters.clients.map(toOption),
  }

  return snapshot
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

export function getSnapshot(producer_id: number): Promise<Snapshot> {
  return api.get("/lots/snapshot", { producer_id }).then(normalizeFilters)
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
