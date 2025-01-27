import { ChargePoint } from "elec-charge-points/types"

export type AddMeterQuery = {
  initial_index_date: string | undefined
  initial_index: number | undefined
  mid_certificate: string | undefined
  charge_point_id: number
}

export type ChangeMeasureReferencePointQuery = {
  measure_reference_point_id: string | undefined
  measure_date: string | undefined
  charge_point_id: number
}

export type UpdateChargePointQuery = {
  charge_point_id: ChargePoint["charge_point_id"]
  initial_index?: ChargePoint["initial_index"]
}
