import api, { type Api } from "common/services/api"

export function deleteChargePointsApplication(
  entity_id: number,
  meter_reading_application_id: number
) {
  return api.post<Api<void>>("elec/cpo/meter-readings/delete-application", {
    entity_id,
    id: meter_reading_application_id,
  })
}
