import api, { Api } from "common/services/api"
import {
  DoubleCountingDetails,
  ApplicationSnapshot,
  ApplicationsOverview,
  QuotaDetails,
  QuotaOverview,
  DoubleCountingUploadErrors,
  CheckDoubleCountingFilesResponse,
} from "./types"

export function getDoubleCountingSnapshot() {
  return api.get<Api<ApplicationSnapshot>>(
    "/v3/doublecount/admin/applications-snapshot"
  )
}

export function getAllDoubleCountingApplications(year: number) {
  return api.get<Api<ApplicationsOverview>>("/v5/admin/double-counting/applications", {
    params: { year },
  })
}

export function getDoubleCountingApplication(dca_id: number) {
  return api.get<Api<DoubleCountingDetails>>(
    "/v3/doublecount/admin/application",
    {
      params: { dca_id },
    }
  )
}

export function approveDoubleCountingQuotas(
  dca_id: number,
  approved_quotas: number[][]
) {
  return api.post("/v3/doublecount/admin/application/update-approved-quotas", {
    dca_id,
    approved_quotas: JSON.stringify(approved_quotas),
  })
}

export function approveDoubleCountingApplication(
  validator_entity_id: number | undefined,
  dca_id: number
) {
  return api.post("/v3/doublecount/admin/approve", {
    validator_entity_id: validator_entity_id,
    dca_id: dca_id,
  })
}

export function rejectDoubleCountingApplication(
  validator_entity_id: number | undefined,
  dca_id: number
) {
  return api.post("/v3/doublecount/admin/reject", {
    validator_entity_id: validator_entity_id,
    dca_id: dca_id,
  })
}

export function getQuotasSnapshot(year: number) {
  return api.get<Api<QuotaOverview[]>>(
    "/v3/doublecount/admin/quotas-snapshot",
    {
      params: { year },
    }
  )
}

export function getQuotaDetails(year: number, production_site_id: number) {
  return api.get<Api<QuotaDetails[]>>("/v3/doublecount/admin/quotas", {
    params: { year, production_site_id },
  })
}

export function uploadDoubleCountingDecision(dca_id: number, file: File) {
  return api.post("/v3/doublecount/admin/upload-decision", { file })
}

export function checkDoubleCountingFiles(entity_id: number, files: FileList) {
  const res = api.post<Api<CheckDoubleCountingFilesResponse>>(
    "/v5/admin/double-counting/applications/check-files",
    { entity_id, files }
  )
  return res
}

export function addDoubleCountingApplication(
  entity_id: number,
  production_site_id: number,
  producer_id: number,
  file: File
) {
  console.log('producer_id:', producer_id)
  console.log('production_site_id:', production_site_id)
  return api.post("/v5/admin/double-counting/applications/add", {
    entity_id,
    production_site_id,
    producer_id,
    file,
  })
}
