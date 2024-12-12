import api, { Api, download } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import {
  AgreementDetails,
  CheckDoubleCountingFilesResponse,
  DoubleCountingAgreementsOverview,
} from "../double-counting/types"

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
  // dca_id: number,
  approved_quotas: number[][]
) {
  return apiFetch.POST(
    "/double-counting/applications/update-approved-quotas/",
    {
      params: { query: { entity_id } },
      body: { approved_quotas },
    }
  )
}

export function downloadDoubleCountingApplication(
  entity_id: number | undefined,
  dca_id: number,
  industrial_wastes?: string
) {
  return download("/double-counting/admin/applications/export", {
    entity_id,
    dca_id,
    ...(industrial_wastes ? { di: industrial_wastes } : {}),
  })
}

export function approveDoubleCountingApplication(
  entity_id: number | undefined,
  dca_id: number
) {
  return api.post("/double-counting/admin/applications/approve", {
    entity_id,
    dca_id,
  })
}

export function rejectDoubleCountingApplication(
  entity_id: number,
  dca_id: number
) {
  return api.post("/double-counting/admin/applications/reject", {
    entity_id,
    dca_id: dca_id,
  })
}

// AGREEMENTS

export function downloadDoubleCountingAgreementList(entity_id: number) {
  return download("/double-counting/admin/agreements", {
    entity_id,
    as_excel_file: true,
  })
}

export function getDoubleCountingAgreementList(
  entity_id: number,
  order_by?: string,
  direction?: string
) {
  return api.get<Api<DoubleCountingAgreementsOverview>>(
    "/double-counting/admin/agreements",
    { params: { entity_id, order_by, direction } }
  )
}

export function getDoubleCountingAgreement(
  entity_id: number,
  agreement_id: number
) {
  return api.get<Api<AgreementDetails>>(
    "/double-counting/admin/agreements/details",
    {
      params: { entity_id, agreement_id },
    }
  )
}

export function checkDoubleCountingFiles(entity_id: number, files: FileList) {
  const res = api.post<Api<CheckDoubleCountingFilesResponse>>(
    "/double-counting/admin/applications/check-files",
    { entity_id, files }
  )
  return res
}
