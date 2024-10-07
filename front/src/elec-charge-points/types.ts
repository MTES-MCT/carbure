export type ChargePointsSnapshot = {
  charge_point_applications: number
  meter_reading_applications: number
  charge_points: number

  // Data used for status tab in "charge points" page
  pending: number
  audit_in_progress: number
  accepted: number
}
