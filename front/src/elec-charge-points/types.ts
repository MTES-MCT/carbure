export type ChargePointsSnapshot = {
  charge_point_applications: number
  meter_reading_applications: number
  charge_points: number

  // Data used for status tab in "charge points" page
  charge_points_pending: number
  charge_points_audit_in_progress: number
  charge_points_accepted: number
}
