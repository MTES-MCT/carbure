import { apiTypes } from "common/services/api-fetch.types"
import { MalfunctionTypesEnum as MalfunctionTypes } from "api-schema"

export { MalfunctionTypes }

export type BiomethaneEnergy = apiTypes["BiomethaneEnergy"]
export type BiomethaneEnergyInputRequest =
  apiTypes["BiomethaneEnergyInputRequest"]
export type BiomethaneEnergyMonthlyReport =
  apiTypes["BiomethaneEnergyMonthlyReport"]
export type BiomethaneEnergyMonthlyReportDataRequest =
  apiTypes["MonthlyReportDataRequest"]
