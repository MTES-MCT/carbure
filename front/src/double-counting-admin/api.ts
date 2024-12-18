import { download } from "common/services/api"
import {
  api as apiFetch,
  download as downloadFetch,
} from "common/services/api-fetch"
import { PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by } from "api-schema"

// GLOBAL

export function getSnapshot(entity_id: number) {
  return apiFetch.GET("/double-counting/snapshot/", {
    params: { query: { entity_id } },
  })
}

// APPLICATIONS

export function getDoubleCountingApplicationList(entity_id: number) {
  return apiFetch.GET("/double-counting/applications/list-admin/", {
    params: { query: { entity_id } },
  })
}

export function getDoubleCountingApplication(
  entity_id: number,
  dca_id: number
) {
  return apiFetch.GET("/double-counting/applications/{id}/", {
    params: {
      path: { id: dca_id },
      query: { entity_id },
    },
  })
}

export function adminAddDoubleCountingApplication(
  entity_id: number,
  production_site_id: number,
  producer_id: number,
  file: File,
  certificate_id?: string,
  should_replace = false
) {
  return apiFetch.POST("/double-counting/applications/add/", {
    params: { query: { entity_id } },
    body: {
      entity_id,
      producer_id,
      production_site_id,
      certificate_id,
      should_replace,
      file: file as unknown as string, // hacky cast for file upload
    },
  })
}

export function approveDoubleCountingQuotas(
  entity_id: number,
  dca_id: number,
  approved_quotas: number[][]
) {
  return apiFetch.POST(
    "/double-counting/applications/{id}/update-approved-quotas/",
    {
      params: { query: { entity_id }, path: { id: dca_id } },
      body: { approved_quotas },
      bodySerializer: JSON.stringify,
    }
  )
}

export function downloadDoubleCountingApplication(
  entity_id: number | undefined,
  dca_id: number,
  industrial_wastes?: string
) {
  // TODO: rework downloadFetch() to typecheck for endpoints with variable paths
  return download(`/double-counting/applications/export-application`, {
    entity_id,
    dca_id,
    ...(industrial_wastes ? { di: industrial_wastes } : {}),
  })
}

export function approveDoubleCountingApplication(
  entity_id: number,
  dca_id: number
) {
  return apiFetch.POST("/double-counting/applications/approve/", {
    params: { query: { entity_id } },
    body: { dca_id },
  })
}

export function rejectDoubleCountingApplication(
  entity_id: number,
  dca_id: number
) {
  return apiFetch.POST("/double-counting/applications/reject/", {
    params: { query: { entity_id } },
    body: { dca_id },
  })
}

// AGREEMENTS

export function downloadDoubleCountingAgreementList(entity_id: number) {
  return downloadFetch("/double-counting/agreements/export/", {
    entity_id,
  })
}

export function getDoubleCountingAgreementList(
  entity_id: number,
  order_by?: string,
  ordering?: string
) {
  return apiFetch.GET("/double-counting/agreements/agreement-admin/", {
    params: {
      query: {
        entity_id,
        ordering,
        order_by: order_by
          ? [
              order_by as PathsApiDoubleCountingAgreementsGetParametersQueryOrder_by,
            ]
          : undefined,
      },
    },
  })
}

export function getDoubleCountingAgreement(
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

export function checkDoubleCountingFiles(entity_id: number, files: FileList) {
  return apiFetch.POST("/double-counting/applications/check-admin-files/", {
    params: { query: { entity_id } },
    body: { files: files as unknown as string[] }, // type hack for file upload
  })
}
