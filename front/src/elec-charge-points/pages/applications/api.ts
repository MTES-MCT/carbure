import api, { type Api } from "common/services/api"

export function deleteChargePointsApplication(
  entity_id: number,
  charge_point_application_id: number
) {
  return api.post<Api<void>>("elec/cpo/charge-points/delete-application", {
    entity_id,
    id: charge_point_application_id,
  })
}
