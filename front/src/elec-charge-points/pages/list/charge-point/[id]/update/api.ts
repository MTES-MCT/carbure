import api, { Api } from "common/services/api"
import { ChargePoint, ElecMeter } from "elec-charge-points/types"
import {
  AddMeterQuery,
  ChangeMeasureReferencePointQuery,
  UpdateChargePointQuery,
} from "./types"

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

export function deleteMeter(entity_id: number, charge_point_id: number) {
  return api.post<Api<undefined>>("elec/cpo/meters/delete-meter", {
    entity_id,
    charge_point_id,
  })
}

export function changeMeasureReferencePoint(
  entity_id: number,
  query: ChangeMeasureReferencePointQuery
) {
  const { charge_point_id, ...params } = query
  return api.post<Api<undefined>>("elec/cpo/charge-points/update-prm", {
    entity_id,
    ...{
      ...params,
      id: charge_point_id,
    },
  })
}

export function getMetersHistory(entity_id: number, id: ChargePoint["id"]) {
  return api.get<Api<ElecMeter[]>>("elec/cpo/meters", {
    params: {
      entity_id,
      charge_point_id: id,
    },
  })
}

export function deleteChargePoint(entity_id: number, id: ChargePoint["id"]) {
  return api.post("elec/cpo/charge-points/delete", {
    entity_id,
    id,
  })
}

export function updateChargePoint(
  entity_id: number,
  id: ChargePoint["id"],
  query: UpdateChargePointQuery
) {
  return api.post("elec/cpo/charge-points/update-charge-point", {
    entity_id,
    id,
    ...query,
  })
}
