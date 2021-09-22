import api from "common/services/api"
import { DoubleCounting, DoubleCountingDetails } from 'common/types'

export interface AgreementsOverview {
  accepted: {count: number, agreements: DoubleCounting[] }, 
  rejected:  {count: number, agreements: DoubleCounting[] }, 
  expired: {count: number, agreements: DoubleCounting[] },  
  pending: {count: number, agreements: DoubleCounting[] }, 
}

export function getAllDoubleCountingAgreements() {
  return api.get<AgreementsOverview>('/doublecount/admin/agreements')
}

export function getDoubleCountingAgreement(dca_id: number) {
  return api.get<DoubleCountingDetails>('/doublecount/admin/agreement', { dca_id })
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
