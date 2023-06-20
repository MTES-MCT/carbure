import api, { Api } from "common/services/api"
import {
  DoubleCounting,
  DoubleCountingDetails,
  DoubleCountingFileInfo,
  DoubleCountingUploadErrors,
  QuotaDetails
} from "double-counting/types"

export function getDoubleCountingAgreements(entity_id: number) {
  return api.get<Api<DoubleCounting[]>>("/v3/doublecount/agreements", {
    params: { entity_id },
  })
}

export function getDoubleCountingDetails(entity_id: number, dca_id: number) {
  return api.get<Api<DoubleCountingDetails>>("/v3/doublecount/agreement", {
    params: { entity_id, dca_id },
  })
}

export function checkDoubleCountingApplication(entity_id: number, file: File) {
  const res = api.post<Api<{ file: DoubleCountingFileInfo }>>(
    "/v5/double-counting/application/check-file",
    { entity_id, file }
  )
  return res
}

export function uploadDoubleCountingFile(
  entity_id: number,
  production_site_id: number,
  file: File
) {
  const res = api.post<Api<{
    dca_id: number,
    errors?: DoubleCountingUploadErrors
  }>>("/v3/doublecount/upload", {
    entity_id,
    production_site_id,
    file,
  })
  return res
}

export function uploadDoubleCountingDescriptionFile(
  entity_id: number,
  dca_id: number,
  file: File
) {
  return api.post("/v3/doublecount/upload-documentation", {
    entity_id,
    dca_id,
    file,
  })
}

export function addDoubleCountingSourcing(
  entity_id: number,
  dca_id: number,
  year: number,
  metric_tonnes: number,
  feedstock_code: string,
  origin_country_code: string,
  supply_country_code: string,
  transit_country_code: string
) {
  return api.post("/v3/doublecount/agreement/add-sourcing", {
    entity_id,
    dca_id,
    year,
    metric_tonnes,
    feedstock_code,
    origin_country_code,
    supply_country_code,
    transit_country_code,
  })
}

export function updateDoubleCountingSourcing(
  entity_id: number,
  dca_sourcing_id: number,
  metric_tonnes: number
) {
  return api.post("/v3/doublecount/agreement/update-sourcing", {
    entity_id,
    dca_sourcing_id,
    metric_tonnes,
  })
}

export function deleteDoubleCountingSourcing(
  entity_id: number,
  dca_sourcing_id: number
) {
  return api.post("/v3/doublecount/agreement/remove-sourcing", {
    entity_id,
    dca_sourcing_id,
  })
}

export function addDoubleCountingProduction(
  entity_id: number,
  dca_id: number,
  year: number,
  feedstock_code: string,
  biofuel_code: string,
  estimated_production: number,
  max_production_capacity: number,
  requested_quota: number
) {
  return api.post("/v3/doublecount/agreement/add-production", {
    entity_id,
    dca_id,
    year,
    feedstock_code,
    biofuel_code,
    estimated_production,
    max_production_capacity,
    requested_quota,
  })
}

export function updateDoubleCountingProduction(
  entity_id: number,
  dca_production_id: number,
  estimated_production: number,
  max_production_capacity: number,
  requested_quota: number
) {
  return api.post("/v3/doublecount/agreement/update-production", {
    entity_id,
    dca_production_id,
    estimated_production,
    max_production_capacity,
    requested_quota,
  })
}

export function deleteDoubleCountingProduction(
  entity_id: number,
  dca_production_id: number
) {
  return api.post("/v3/doublecount/agreement/remove-production", {
    entity_id,
    dca_production_id,
  })
}

export function getQuotaDetails(entity_id: number, dca_id: number) {
  return api.get<Api<QuotaDetails[]>>("/v3/doublecount/quotas", {
    params: { entity_id, dca_id },
  })
}
