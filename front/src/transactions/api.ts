import {
  Transaction,
  Lots,
  LotStatus,
  Snapshot,
  Filters,
  LotDetails,
} from "common/types"
import { FilterSelection } from "transactions/hooks/query/use-filters"

import api from "common/services/api"
import differenceInCalendarMonths from "date-fns/differenceInCalendarMonths"

export function toOption(value: string) {
  return { value, label: value }
}

export function hasDeadline(tx: Transaction, deadline: string): boolean {
  if (!tx || tx.lot.status !== "Draft") return false

  const deadlineDate = new Date(deadline)

  const deliveryDate = tx?.delivery_date
    ? new Date(tx.delivery_date)
    : new Date()

  return differenceInCalendarMonths(deadlineDate, deliveryDate) === 1
}

// give the same type to all filters in order to render them easily
function normalizeFilters(snapshot: any): Snapshot {
  Object.values(Filters).forEach((key) => {
    const filter = snapshot.filters[key]

    if (filter && typeof filter[0] === "string") {
      snapshot.filters[key] = filter.map(toOption)
    }
  })

  snapshot.years = snapshot.years.map(toOption)

  return snapshot
}

// extract the status name from the lot details
export function getStatus(transaction: Transaction, entity: number): LotStatus {
  const status = transaction.lot.status.toLowerCase()
  const delivery = transaction.delivery_status

  const isVendor = transaction.carbure_vendor?.id === entity
  const isClient = transaction.carbure_client?.id === entity

  if (status === "draft") {
    return LotStatus.Draft
  } else if (status === "validated") {
    if (delivery === "A") {
      return LotStatus.Accepted
    }
    // OPERATEUR
    else if (isClient && ["N", "AA", "AC"].includes(delivery)) {
      return LotStatus.Inbox
    }
    // PRODUCTEUR
    else if (isVendor) {
      if (["N", "AA"].includes(delivery)) {
        return LotStatus.Validated
      } else if (["AC", "R"].includes(delivery)) {
        return LotStatus.ToFix
      }
    }
  }

  return LotStatus.Weird
}

export function getSnapshot(entityID: number, year: number): Promise<Snapshot> {
  return api
    .get("/lots/snapshot", { entity_id: entityID, year })
    .then(normalizeFilters)
}

export function getLots(
  status: LotStatus,
  entityID: number,
  filters: FilterSelection["selected"],
  year: number,
  page: number,
  limit: number,
  query: string,
  sortBy: string,
  order: string,
  invalid: boolean,
  deadline: boolean
): Promise<Lots> {
  const params = {
    ...filters,
    entity_id: entityID,
    from_idx: page * limit,
    sort_by: sortBy,
    status,
    year,
    limit,
    query,
    order,
    invalid,
    deadline,
  }

  return api.get("/lots/", params)
}

export function getDetails(
  entityID: number,
  transactionID: number
): Promise<LotDetails> {
  return api.get("/lots/details", { entity_id: entityID, tx_id: transactionID })
}

export function downloadLots(
  status: LotStatus,
  producerID: number,
  filters: FilterSelection["selected"],
  year: number,
  query: string,
  sortBy: string,
  order: string
) {
  return api.download("/lots", {
    ...filters,
    entity_id: producerID,
    sort_by: sortBy,
    status,
    year,
    query,
    order,
    export: true,
  })
}

export function addLot(entityID: number, params: any): Promise<Transaction> {
  return api.post("/lots/add", {
    entity_id: entityID,
    ...params,
  })
}

export function uploadLotFile(entityID: number, file: File): Promise<void> {
  return api.post("/lots/upload", {
    entity_id: entityID,
    file,
  })
}

export function uploadMassBalanceFile(
  entityID: number,
  file: File
): Promise<void> {
  return api.post("/stocks/upload-mass-balance", {
    entity_id: entityID,
    file,
  })
}

export function uploadOperatorLotFile(
  entityID: number,
  file: File
): Promise<void> {
  return api.post("/lots/upload-blend", {
    entity_id: entityID,
    file,
  })
}

export function downloadTemplateSimple(entityID: number) {
  return api.download("/lots/download-template-simple", {
    entity_id: entityID,
  })
}

export function downloadTemplateAdvanced(entityID: number) {
  return api.download("/lots/download-template-advanced", {
    entity_id: entityID,
  })
}

export function downloadTemplateMassBalanceCarbureID(entityID: number) {
  return api.download("/stocks/download-template-mass-balance", {
    entity_id: entityID,
  })
}

export function downloadTemplateMassBalanceBCGHG(entityID: number) {
  return api.download("/stocks/download-template-mass-balance-bcghg", {
    entity_id: entityID,
  })
}

export function downloadTemplateOperator(entityID: number) {
  return api.download("/lots/download-template-blend", {
    entity_id: entityID,
  })
}

export function downloadTemplateTrader(entityID: number) {
  return api.download("/lots/download-template-trader", {
    entity_id: entityID,
  })
}

export function updateLot(
  entityID: number,
  transactionID: number,
  params: any
): Promise<boolean> {
  return api.post("/lots/update", {
    entity_id: entityID,
    tx_id: transactionID,
    ...params,
  })
}

export function duplicateLot(entityID: number, transactionID: number) {
  return api.post("/lots/duplicate", {
    entity_id: entityID,
    tx_id: transactionID,
  })
}

export function deleteLots(entityID: number, transactionIDs: number[]) {
  return api.post("/lots/delete", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function validateLots(entityID: number, transactionIDs: number[]) {
  return api.post("/lots/validate", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function acceptLots(entityID: number, transactionIDs: number[]) {
  return api.post("/lots/accept", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function acceptLotsWithReserve(
  entityID: number,
  transactionIDs: number[]
) {
  return api.post("/lots/accept-with-reserves", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function rejectLots(
  entityID: number,
  transactionIDs: number[],
  comment: string
) {
  return api.post("/lots/reject", {
    entity_id: entityID,
    tx_ids: transactionIDs,
    comment,
  })
}

export function commentLot(
  entityID: number,
  transactionID: number,
  comment: string,
  topic: string
) {
  return api.post("/lots/comment", {
    entity_id: entityID,
    tx_id: transactionID,
    comment_type: topic,
    comment,
  })
}

export function validateAndCommentLot(
  entityID: number,
  transactionID: number,
  comment: string
) {
  const validating = validateLots(entityID, [transactionID])
  const commenting = commentLot(entityID, transactionID, comment, "both")

  return Promise.all([validating, commenting])
}

export function acceptAndCommentLot(
  entityID: number,
  transactionID: number,
  comment: string,
  topic: string
) {
  const accepting = acceptLotsWithReserve(entityID, [transactionID])
  const commenting = commentLot(entityID, transactionID, comment, topic)

  return Promise.all([accepting, commenting])
}

export function deleteAllDraftLots(entityID: number, year: number) {
  return api.post("/lots/delete-all-drafts", {
    entity_id: entityID,
    year,
  })
}

export function validateAllDraftLots(entityID: number, year: number) {
  return api.post("/lots/validate-all-drafts", {
    entity_id: entityID,
    year,
  })
}

export function acceptAllInboxLots(entityID: number, year: number) {
  return api.post("/lots/accept-all", {
    entity_id: entityID,
    year,
  })
}

export function rejectAllInboxLots(
  entityID: number,
  year: number,
  comment: string
) {
  return api.post("/lots/reject-all", {
    entity_id: entityID,
    year,
    comment,
  })
}

export function getLotsOutSummary(entityID: number) {
  return api.get("/lots/summary-out", {
    entity_id: entityID,
  })
}

export function getLotsInSummary(entityID: number) {
  return api.get("/lots/summary-in", {
    entity_id: entityID,
  })
}

export function declareLots(entity_id: number, period: string) {
  return api.post("/lots/declaration", { entity_id, period })
}

// ADMIN

export function getAdminSnapshot(
  entityID: number,
  year: number
): Promise<Snapshot> {
  return api
    .get("/admin/lots/snapshot", { entity_id: entityID, year })
    .then(normalizeFilters)
}

export function getAdminLots(
  status: LotStatus,
  entityID: number,
  filters: FilterSelection["selected"],
  year: number,
  page: number,
  limit: number,
  query: string,
  sortBy: string,
  order: string,
  invalid: boolean,
  deadline: boolean
): Promise<Lots> {
  const params = {
    ...filters,
    entity_id: entityID,
    from_idx: page * limit,
    sort_by: sortBy,
    status,
    year,
    limit,
    query,
    order,
  }

  return api.get("/admin/lots", params)
}

export function downloadAdminLots(
  status: LotStatus,
  producerID: number,
  filters: FilterSelection["selected"],
  year: number,
  query: string,
  sortBy: string,
  order: string
) {
  return api.download("/admin/lots", {
    ...filters,
    entity_id: producerID,
    sort_by: sortBy,
    status,
    year,
    query,
    order,
    export: true,
  })
}

export function getAdminDetails(
  entityID: number,
  transactionID: number
): Promise<LotDetails> {
  return api.get("/admin/lots/details", {
    entity_id: entityID,
    tx_id: transactionID,
  })
}
