import {
  Transaction,
  Lots,
  LotStatus,
  Snapshot,
  LotDetails,
} from "common/types"
import { FilterSelection } from "transactions/hooks/query/use-filters"

import api from "common/services/api"
import { flattenSummary, normalizeFilters } from "./helpers"

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

export async function validateAndCommentLot(
  entityID: number,
  transactionID: number,
  comment: string
) {
  const commenting = await commentLot(entityID, transactionID, comment, "both")
  const validating = await validateLots(entityID, [transactionID])

  return [validating, commenting]
}

export async function acceptAndCommentLot(
  entityID: number,
  transactionID: number,
  comment: string,
  topic: string
) {
  const commenting = await commentLot(entityID, transactionID, comment, topic)
  const accepting = await acceptLotsWithReserve(entityID, [transactionID])

  return [accepting, commenting]
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

export function getLotsOutSummary(entityID: number, lot_status: LotStatus, period: string, delivery_status: string[]) {
  return api.get("/lots/summary-out", {
    entity_id: entityID,
    lot_status,
    period,
    delivery_status,
  })
}

export function getLotsInSummary(entityID: number) {
  return api.get("/lots/summary-in", {
    entity_id: entityID,
  })
}

export function getDeclarationSummary(
  entity_id: number,
  period_year: number,
  period_month: number
) {
  return api
    .post("/lots/declaration-summary", {
      entity_id,
      period_year,
      period_month,
    })
    .then((res) => ({
      declaration: res.declaration,
      in: res.in ? flattenSummary(res.in) : null,
      out: res.out ? flattenSummary(res.out) : null,
    }))
}

export function validateDeclaration(
  entity_id: number,
  period_year: number,
  period_month: number
) {
  return api.post("/lots/validate-declaration", {
    entity_id,
    period_year,
    period_month,
  })
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
