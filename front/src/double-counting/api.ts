import api, { Api } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import {
  AgreementDetails,
  DoubleCountingApplicationDetails,
  DoubleCountingFileInfo,
} from "double-counting/types"

export function getDoubleCountingAgreements(entity_id: number) {
  return apiFetch.GET("/double-counting/agreements/", {
    params: { query: { entity_id } },
  })
}

export function getDoubleCountingAgreementsPublicList() {
  return apiFetch.GET("/double-counting/agreements/agreement-public/", {})
}

export function getDoubleCountingApplicationDetails(
  entity_id: number,
  dca_id: number
) {
  return api.get<Api<DoubleCountingApplicationDetails>>(
    "/double-counting/applications/details",
    {
      params: { entity_id, dca_id },
    }
  )
}

export function checkDoubleCountingApplication(entity_id: number, file: File) {
  const res = api.post<Api<{ file: DoubleCountingFileInfo }>>(
    "/double-counting/applications/check-file",
    { entity_id, file }
  )
  return res
}

export function getDoubleCountingAgreementDetails(
  entity_id: number,
  agreement_id: number
) {
  return api.get<Api<AgreementDetails>>("/double-counting/agreements/details", {
    params: { entity_id, agreement_id },
  })
}

export function producerAddDoubleCountingApplication(
  entity_id: number,
  producer_id: number,
  production_site_id: number,
  file: File,
  should_replace = false
) {
  return api.post("/double-counting/applications/add", {
    entity_id,
    producer_id,
    production_site_id,
    file,
    should_replace,
  })
}
