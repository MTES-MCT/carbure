import api, { Api } from "common/services/api"
import { ChargePoint } from "elec-charge-points/types"
import { AddMeterQuery } from "./types"

export function getChargePointDetail(
  entity_id: number,
  charge_point_id: number
) {
  return api.get<Api<ChargePoint>>("elec/cpo/charge-points/details", {
    params: { entity_id, charge_point_id },
  })
}

export function addMeter(entity_id: number, query: AddMeterQuery) {
  const { charge_point_id, ...params } = query
  return api.post<Api<undefined>>("elec/cpo/meters/add-meter", {
    entity_id,
    ...{
      ...params,
      charge_point: charge_point_id,
    },
  })
}
