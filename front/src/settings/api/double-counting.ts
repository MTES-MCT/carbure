import api, { Api } from "common/services/api"
import {
  DoubleCountingApplicationOverview,
  DoubleCountingApplicationDetails,
  DoubleCountingFileInfo,
  DoubleCountingUploadErrors,
  QuotaDetails
} from "double-counting/types"

export function getDoubleCountingApplications(entity_id: number) {
  return api.get<Api<DoubleCountingApplicationOverview[]>>("/v3/doublecount/applications", {
    params: { entity_id },
  })
}

export function getDoubleCountingApplicationDetails(entity_id: number, dca_id: number) {
  return api.get<Api<DoubleCountingApplicationDetails>>("/v3/doublecount/application", {
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
  return api.post("/v3/doublecount/application/add-sourcing", {
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
  return api.post("/v3/doublecount/application/update-sourcing", {
    entity_id,
    dca_sourcing_id,
    metric_tonnes,
  })
}

export function deleteDoubleCountingSourcing(
  entity_id: number,
  dca_sourcing_id: number
) {
  return api.post("/v3/doublecount/application/remove-sourcing", {
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
  return api.post("/v3/doublecount/application/add-production", {
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
  return api.post("/v3/doublecount/application/update-production", {
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
  return api.post("/v3/doublecount/application/remove-production", {
    entity_id,
    dca_production_id,
  })
}

export function getQuotaDetails(entity_id: number, dca_id: number) {
  return api.get<Api<QuotaDetails[]>>("/v3/doublecount/quotas", {
    params: { entity_id, dca_id },
  })
}
