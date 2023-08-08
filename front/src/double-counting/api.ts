import api, { Api } from "common/services/api"
import {
  DoubleCountingApplicationDetails,
  DoubleCountingApplicationSnapshot,
  DoubleCountingApplicationsOverview,
  QuotaDetails,
  DoubleCountingAgreementOverview,
  DoubleCountingUploadErrors,
  CheckDoubleCountingFilesResponse,
  DoubleCountingSnapshot,
  DoubleCountingAgreementsOverview,
  AgreementDetails,
} from "./types"

// GLOBAL

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/admin/double-counting/years", {
    params: { entity_id },
  })
}



export function getSnapshot(entity_id: number) {
  return api.get<Api<DoubleCountingSnapshot>>("/v5/admin/double-counting/snapshot", {
    params: { entity_id },
  })
}
// export function getDoubleCountingSnapshot() {
//   return api.get<Api<ApplicationSnapshot>>(
//     "/v3/doublecount/admin/applications-snapshot"
//   )
// }

// APPLICATIONS


export function getAllDoubleCountingApplications(entity_id: number) {
  return api.get<Api<DoubleCountingApplicationsOverview>>("/v5/admin/double-counting/applications", {
    params: { entity_id },
  })
}

export function getDoubleCountingApplication(entity_id: number, dca_id: number) {
  return api.get<Api<DoubleCountingApplicationDetails>>(
    "/v5/admin/double-counting/applications/details",
    {
      params: { entity_id, dca_id },
    }
  )
}


export function addDoubleCountingApplication(
  entity_id: number,
  production_site_id: number,
  producer_id: number,
  file: File,
  should_replace: boolean = false
) {

  return api.post("/v5/admin/double-counting/applications/add", {
    entity_id,
    production_site_id,
    producer_id,
    file,
    should_replace
  })
}


export function approveDoubleCountingQuotas(
  entity_id: number,
  dca_id: number,
  approved_quotas: number[][]
) {
  return api.post("/v5/admin/double-counting/applications/update-quotas", {
    entity_id,
    dca_id,
    approved_quotas: JSON.stringify(approved_quotas),
  })
}

export function approveDoubleCountingApplication(
  entity_id: number | undefined,
  dca_id: number
) {
  return api.post("/v5/admin/double-counting/applications/approve", {
    entity_id,
    dca_id,
  })
}

export function rejectDoubleCountingApplication(
  entity_id: number,
  dca_id: number
) {
  return api.post("/v5/admin/double-counting/applications/reject", {
    entity_id,
    dca_id: dca_id,
  })
}

// AGREEMENTS

export function getAgreementList(entity_id: number) {
  return api.get<Api<DoubleCountingAgreementsOverview>>(
    "/v5/admin/double-counting/agreements"
    , { params: { entity_id } })
}

export function getDoubleCountingAgreement(entity_id: number, agreement_id: number) {
  return api.get<Api<AgreementDetails>>(
    "/v5/admin/double-counting/agreements/details",
    {
      params: { entity_id, agreement_id },
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
