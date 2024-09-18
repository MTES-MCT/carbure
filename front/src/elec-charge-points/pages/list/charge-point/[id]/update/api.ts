import api, { Api } from "common/services/api"
import { ChargePoint } from "elec-charge-points/types"

export function getChargePointDetail(
  entity_id: number,
  charge_point_id: number
) {
  return api.get<Api<ChargePoint>>("elec/cpo/charge-points/details", {
    params: { entity_id, charge_point_id },
  })
}
