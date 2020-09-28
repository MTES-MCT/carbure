import api, { ApiPromise } from "./api"
import { Lot, Lots, LotStatus, Snapshot } from "./types"

// give the same form to all filters in order to render them easily
// @TODO change any type
function normalizeFilters(filters: any) {
  for (const key in filters) {
    filters[key] = filters[key].map((filter: any) =>
      typeof filter === "string" ? { key: filter, label: filter } : filter
    )
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

export function getSnapshot(producerID: number): ApiPromise<Snapshot> {
  return api
    .get("/lots/snapshot", { producer_id: producerID })
    .then((snapshot: any) => {
      normalizeFilters(snapshot.data.filters)
      return snapshot
    })
}

export function getLots(
  status: LotStatus,
  producerID: number,
  filters: any, // @TODO
  pagination: { page: number; limit: number }
): ApiPromise<Lots> {
  return api.get("/lots", {
    status,
    producer_id: producerID,
    ...filters,
    from_idx: pagination.page * pagination.limit,
    limit: pagination.limit,
  })
}
