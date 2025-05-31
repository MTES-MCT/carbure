import { api as apiFetch } from "common/services/api-fetch"

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
    body: { file },
  })
}

export function getDoubleCountingAgreementDetails(
  entity_id: number,
  agreement_id: number
) {
  return apiFetch.GET("/double-counting/agreements/{id}/", {
    params: {
      query: { entity_id },
      path: { id: agreement_id },
    },
  })
}

export function producerAddDoubleCountingApplication(
  entity_id: number,
  producer_id: number,
  production_site_id: number,
  file: File,
  industrialWastesFile?: File,
  should_replace = false
) {
  return apiFetch.POST("/double-counting/applications/add/", {
    params: { query: { entity_id } },
    body: {
      entity_id,
      producer_id,
      production_site_id,
      should_replace,
      file,
      industrial_wastes_file: industrialWastesFile,
    },
  })
}

export function getDoubleCountingAgreementDownloadLink(
  entity_id: number,
  agreement_id: number
) {
  return apiFetch.GET("/double-counting/agreements/{id}/download-link/", {
    params: {
      query: { entity_id },
      path: { id: agreement_id },
    },
  })
}

export function updateDoubleCountingApplicationIndustrialWastesFile(
  entity_id: number,
  dca_id: number,
  industrial_wastes_file: File
) {
  return apiFetch.POST(
    "/double-counting/applications/{id}/update-industrial-wastes-file/",
    {
      params: {
        query: { entity_id },
        path: { id: dca_id },
      },
      body: {
        industrial_wastes_file,
      },
    }
  )
}
