import api, { Api } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { AgreementDetails } from "double-counting/types"

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
  return apiFetch.GET("/double-counting/applications/{id}/", {
    params: {
      query: { entity_id },
      path: { id: dca_id },
    },
  })
}

export function checkDoubleCountingApplication(entity_id: number, file: File) {
  return apiFetch.POST("/double-counting/applications/check-file/", {
    params: { query: { entity_id } },
    body: { file: file as unknown as string }, // hack for file upload :/
    bodySerializer: (body) => {
      const formData = new FormData()
      formData.set("file", body?.file ?? "")
      return formData
    },
  })
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
