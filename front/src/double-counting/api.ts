import api, { Api } from "common/services/api"
import {
  DoubleCountingDetails,
  AgreementSnapshot,
  AgreementsOverview,
  QuotaDetails,
  QuotaOverview,
} from "./types"

export function getDoubleCountingSnapshot() {
  return api.get<Api<AgreementSnapshot>>(
    "/v3/doublecount/admin/agreements-snapshot"
  )
}

export function getAllDoubleCountingAgreements(year: number) {
  return api.get<Api<AgreementsOverview>>("/v3/doublecount/admin/agreements", {
    params: { year },
  })
}

export function getDoubleCountingAgreement(dca_id: number) {
  return api.get<Api<DoubleCountingDetails>>(
    "/v3/doublecount/admin/agreement",
    {
      params: { dca_id },
    }
  )
}

export function approveDoubleCountingQuotas(
  dca_id: number,
  approved_quotas: number[][]
) {
  return api.post("/v3/doublecount/admin/agreement/update-approved-quotas", {
    dca_id,
    approved_quotas: JSON.stringify(approved_quotas),
  })
}

export function approveDoubleCountingAgreement(
  validator_entity_id: number | undefined,
  dca_id: number
) {
  return api.post("/v3/doublecount/admin/approve", {
    validator_entity_id: validator_entity_id,
    dca_id: dca_id,
  })
}

export function rejectDoubleCountingAgreement(
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
  return api.post("/v3/doublecount/admin/upload-decision", { dca_id, file })
}