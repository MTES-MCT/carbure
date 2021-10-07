import api from "common/services/api"
import { DoubleCounting, DoubleCountingDetails, Entity, ProductionSite } from 'common/types'

export interface AgreementSnapshot {
  years: number[]
}

export function getDoubleCountingSnapshot() {
  return api.get<AgreementSnapshot>('/doublecount/admin/agreements-snapshot')
}

export interface AgreementsOverview {
  accepted: { count: number, agreements: DoubleCounting[] },
  rejected: { count: number, agreements: DoubleCounting[] },
  expired: { count: number, agreements: DoubleCounting[] },
  pending: { count: number, agreements: DoubleCounting[] },
  progress: { count: number, agreements: DoubleCounting[] },
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

export interface QuotaOverview {
  producer: Entity
  production_site: ProductionSite
  approved_quota_weight_sum: number
  current_production_weight_sum: number
  nb_quotas: number
  nb_full_quotas: number
  nb_breached_quotas: number
}

export function getQuotasSnapshot(year: number) {
  return api.get<QuotaOverview[]>('/doublecount/admin/quotas-snapshot', { year })
}

export interface QuotaDetails {}

export function getQuotaDetails() {
  return api.get<QuotaDetails[]>('/doublecount/admin/')
}