import { CBQueryParams, CBQueryResult } from "common/hooks/query-builder"
import { ChargePoint } from "elec-charge-points/types"

export type ChargePointsListQuery = CBQueryParams

export type ChargePointsListData = CBQueryResult & {
  elec_charge_points: ChargePoint[]
}

export enum ChargePointFilter {
  MeasureDate = "latest_meter_reading_month",
  ChargePointId = "charge_point_id",
  StationId = "station_id",
  ConcernedByReadingMeter = "is_article_2",
}
