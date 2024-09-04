import { CBQueryParams, CBQueryResult } from "common/hooks/query-builder"

export type ChargePointsListQuery = CBQueryParams

export type ChargePointsListData = CBQueryResult & {
  elec_charge_points: ChargePoint[]
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
  application_date?: string
  charge_point_id: number
  station_id: number
  current_type?: ChargePointType
  measure_date: string | null
  measure_energy: number
  installation_date: string
  concerned_by_reading_meter?: boolean // Revoir le naming
  status: ChargePointStatus
}
export enum ChargePointFilter {
  // Status = "status",
  MeasureDate = "measure_date",
  ChargePointId = "charge_point_id",
  StationId = "station_id",
  ConcernedByReadingMeter = "concerned_by_reading_meter",
}
