import { company } from "common/__test__/data"
import { EntityDetails } from "companies-admin/types"

const companyPreview: EntityDetails = {
  entity: company,
  users: 1,
  requests: 1,
  depots: 1,
  production_sites: 1,
  certificates: 1,
  certificates_pending: 1,
  double_counting: 1,
  double_counting_requests: 1,
  charge_points_accepted: 1,
  charge_points_pending: 1,
  meter_readings_pending: 1,
  meter_readings_accepted: 1,
}
export const companiesSummary: EntityDetails[] = [
  companyPreview,
  companyPreview,
]
