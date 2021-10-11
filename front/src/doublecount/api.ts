import api from "common/services/api"
import { DoubleCountingDetails, AgreementSnapshot, AgreementsOverview, QuotaDetails, QuotaOverview } from './types'

export function getDoubleCountingSnapshot() {
  return api.get<AgreementSnapshot>('/doublecount/admin/agreements-snapshot')
}

export function getAllDoubleCountingAgreements(year: number) {
  return api.get<AgreementsOverview>('/doublecount/admin/agreements', { year })
}

export function getDoubleCountingAgreement(dca_id: number) {
  return api.get<DoubleCountingDetails>('/doublecount/admin/agreement', { dca_id })
}

export function approveDoubleCountingQuotas(dca_id: number, approved_quotas: number[][]) {
  return api.post('/doublecount/admin/agreement/update-approved-quotas', { dca_id, approved_quotas: JSON.stringify(approved_quotas) })
}

export function approveDoubleCountingAgreement(
  validator_entity_id: number | undefined,
  dca_id: number
) {
  return api.post("/doublecount/admin/approve", {
    validator_entity_id: validator_entity_id,
    dca_id: dca_id,
  })
}

export function rejectDoubleCountingAgreement(
  validator_entity_id: number | undefined,
  dca_id: number
) {
  return api.post("/doublecount/admin/reject", {
    validator_entity_id: validator_entity_id,
    dca_id: dca_id,
  })
}

export function getQuotasSnapshot(year: number) {
  return api.get<QuotaOverview[]>('/doublecount/admin/quotas-snapshot', { year })
}

export function getQuotaDetails(year: number, production_site_id: number) {
  return api.get<QuotaDetails[]>('/doublecount/admin/quotas', { year, production_site_id })
}