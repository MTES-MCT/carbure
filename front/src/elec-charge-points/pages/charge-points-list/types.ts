import { CBQueryParams, CBQueryResult } from "common/hooks/query-builder"

export type ChargePointsListQuery = CBQueryParams

export type ChargePointsListData = CBQueryResult & {
  charge_points_list: ChargePoint[]
}

export enum ChargePointStatus {
  Pending = "PENDING",
  AuditInProgress = "AUDIT_IN_PROGRESS",
  Accepted = "ACCEPTED",
}

export enum ChargePointType {
  AC = "AC", // courant alternatif
  DC = "DC", // courant continu
}

export type ChargePoint = {
  id: number
  validation_date?: string
  charge_point_id: number
  station_id: number
  current_type?: ChargePointType
  last_measure_energy: number
  concerned_by_reading_meter?: boolean // Revoir le naming
  status: ChargePointStatus
}
export enum ChargePointFilter {
  ValidationDate = "validation_date",
  ChargePointId = "charge_point_id",
  StationId = "Identifiant station",
  ConcernedByReadingMeter = "concerned_by_reading_meter",
}
