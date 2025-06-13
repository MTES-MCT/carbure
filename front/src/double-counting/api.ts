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
  extraFiles?: File[],
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
      extra_files: extraFiles,
    },
  })
}

export function uploadDoubleCountingApplicationFiles(
  entity_id: number,
  application_id: number,
  extra_files: File[]
) {
  return apiFetch.POST("/double-counting/applications/{id}/upload-files/", {
    params: {
      query: { entity_id },
      path: { id: application_id },
    },
    body: { extra_files },
  })
}

export function deleteDoubleCountingApplicationFile(
  entity_id: number,
  application_id: number,
  file_id: number
) {
  return apiFetch.DELETE(
    "/double-counting/applications/{id}/files/{file_id}/",
    {
      params: {
        query: { entity_id },
        path: { id: application_id, file_id },
      },
    }
  )
}
