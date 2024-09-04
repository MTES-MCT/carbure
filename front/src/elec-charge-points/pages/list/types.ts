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
  status: ChargePointStatus
  is_article_2: boolean // If a charge point is NOT concerned by a reading meter
}
export enum ChargePointFilter {
  MeasureDate = "measure_date",
  ChargePointId = "charge_point_id",
  StationId = "station_id",
  ConcernedByReadingMeter = "is_article_2",
}
