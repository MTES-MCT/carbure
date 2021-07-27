import { TFunction } from "react-i18next"
import {
  Transaction,
  Lots,
  Filters,
  Snapshot,
  LotDetails,
  TransactionQuery,
  TransactionSummary,
} from "common/types"
import { Option } from "common/components/select"
import api from "common/services/api"
import {
  normalizeSummary,
  normalizeFilter,
  normalizeSnapshot,
  filterOutsourcedDepots,
  normalizeGeneralSummary,
} from "./helpers"

export function getSnapshot(
  entityID: number,
  year: number,
  t: TFunction
): Promise<Snapshot> {
  return api
    .get("/lots/snapshot", { entity_id: entityID, year })
    .then((s) => normalizeSnapshot(s, t))
    .then(filterOutsourcedDepots)
}

export function getFilters(
  field: Filters,
  params: TransactionQuery,
  t: TFunction
): Promise<Option[]> {
  return api
    .get("/lots/filters", { field, ...params, limit: null, from_idx: 0 })
    .then((filter) => normalizeFilter(field, filter, t))
}

export function getLots(params: TransactionQuery): Promise<Lots> {
  return api.get("/lots/", params)
}

export function getLotsSummary(
  query: TransactionQuery,
  selection: number[],
  short?: boolean
): Promise<TransactionSummary> {
  return api
    .get("/lots/summary", {
      ...query,
      short,
      limit: null,
      from_idx: 0,
      selection,
    })
    .then(normalizeSummary)
}

export function getDetails(
  entityID: number,
  transactionID: number
): Promise<LotDetails> {
  return api.get("/lots/details", { entity_id: entityID, tx_id: transactionID })
}

export function downloadLots(filters: TransactionQuery) {
  return api.download("/lots", {
    ...filters,
    page: 0,
    limit: null,
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
      ...normalizeSummary(res),
      remaining: res.remaining,
      declaration: res.declaration,
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

export function forwardLots(
  entityID: number,
  transactionIDs: number[]
): Promise<any> {
  return api.post("/lots/forward", {
    entity_id: entityID,
    tx_ids: transactionIDs,
  })
}

export function amendLot(entity_id: number, tx_id: number) {
  return api.post("/lots/amend-lot", { entity_id, tx_id })
}

export async function amendAndCommentLot(
  entity_id: number,
  tx_id: number,
  comment: string
) {
  const commenting = await commentLot(entity_id, tx_id, comment, "both")
  const amending = await amendLot(entity_id, tx_id)
  return [amending, commenting]
}

// ADMIN

export function getAdminSnapshot(
  entityID: number,
  year: number,
  t: TFunction
): Promise<Snapshot> {
  return api
    .get("/admin/lots/snapshot", { entity_id: entityID, year })
    .then((s) => normalizeSnapshot(s, t))
}

export function getAdminFilters(
  field: Filters,
  params: TransactionQuery,
  t: TFunction
): Promise<Option[]> {
  return api
    .get("/admin/lots/filters", { field, ...params, limit: null, from_idx: 0 })
    .then((filter) => normalizeFilter(field, filter, t))
}

export function getAdminLots(filters: TransactionQuery): Promise<Lots> {
  return api.get("/admin/lots", filters)
}

export function downloadAdminLots(filters: TransactionQuery) {
  return api.download("/admin/lots", {
    ...filters,
    page: 0,
    limit: null,
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

export function getAdminSummary(
  query: TransactionQuery,
  selection: number[],
  short?: boolean
): Promise<TransactionSummary> {
  return api
    .get("/admin/lots/summary", {
      ...query,
      short,
      limit: null,
      from_idx: 0,
      selection,
    })
    .then(normalizeGeneralSummary)
}

export function postHideAlerts(alertIDs: number[]): Promise<any> {
  return api.post("/admin/lots/ack-alerts", {
    alert_ids: alertIDs,
  })
}

export function postHighlightAlerts(alertIDs: number[]): Promise<any> {
  return api.post("/admin/lots/highlight-alerts", {
    alert_ids: alertIDs,
  })
}

export function hideAdminLots(entity_id: number, tx_ids: number[]) {
  return api.post("/admin/lots/hide-transactions", { entity_id, tx_ids })
}

export function highlightAdminLots(
  entity_id: number,
  tx_ids: number[],
  notify_auditor?: boolean
) {
  return api.post("/admin/lots/highlight-transactions", {
    entity_id,
    tx_ids,
    notify_auditor,
  })
}

// AUDITOR

export function getAuditorSnapshot(
  entity_id: number,
  year: number,
  t: TFunction
) {
  return api
    .get<Snapshot>("/auditor/snapshot", { entity_id, year })
    .then((s) => normalizeSnapshot(s, t))
}

export function getAuditorFilters(
  field: Filters,
  params: TransactionQuery,
  t: TFunction
): Promise<Option[]> {
  return api
    .get("/auditor/filters", { field, ...params, limit: null, from_idx: 0 })
    .then((filter) => normalizeFilter(field, filter, t))
}

export function getAuditorLots(params: TransactionQuery) {
  return api.get<Lots>("/auditor/lots", params)
}

export function getAuditorSummary(
  query: TransactionQuery,
  selection: number[],
  short?: boolean
): Promise<TransactionSummary> {
  return api
    .get("/auditor/summary", {
      ...query,
      short,
      limit: null,
      from_idx: 0,
      selection,
    })
    .then(normalizeGeneralSummary)
}

export function getAuditorDetails(entity_id: number, tx_id: number) {
  return api.get<LotDetails>("/auditor/details", { entity_id, tx_id })
}

export function downloadAuditorLots(filters: TransactionQuery) {
  return api.download("/auditor/lots", {
    ...filters,
    page: 0,
    limit: null,
    export: true,
  })
}

export function hideAuditorLots(entity_id: number, tx_ids: number[]) {
  return api.post("/auditor/lots/hide-transactions", { entity_id, tx_ids })
}

export function highlightAuditorLots(
  entity_id: number,
  tx_ids: number[],
  notify_admin?: boolean
) {
  return api.post("/auditor/lots/highlight-transactions", {
    entity_id,
    tx_ids,
    notify_admin,
  })
}

export function addAdminComment(tx_ids: number[], comment: string) {
  return api.post("/admin/lots/comment", { tx_ids, comment })
}

export function deleteAdminLots(tx_ids: number[]) {
  return api.post('/admin/lots/delete', { tx_ids })
}