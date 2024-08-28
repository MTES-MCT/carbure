import { CBQueryParams, CBQueryResult } from "common/hooks/query-builder"

export type ChargePointsSnapshot = {
  charge_point_applications: number
  meter_reading_applications: number
  charge_points: number

  // Data used for status tab in "charge points" page
  charge_points_pending: number
  charge_points_audit_in_progress: number
  charge_points_accepted: number
}

export type ChargePointsListQuery = CBQueryParams

export type ChargePointsListData = CBQueryResult & {}

export enum ChargePointsStatus {
  Pending = "PENDING",
  AuditInProgress = "AUDIT_IN_PROGRESS",
  Accepted = "ACCEPTED",
}
