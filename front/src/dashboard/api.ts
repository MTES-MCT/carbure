import api, { Api } from "common/services/api"
import { getLotFilters } from "controls/api/admin"
import { Filter } from "transactions/types"
import { DashboardDeclaration } from "./types"

export function getDeclarations(entity_id: number, period: string) {
  console.log("VERYUNSURE 97")
  return api.get<Api<DashboardDeclaration[]>>(
    "transactions/admin/declarations",
    {
      params: { entity_id, period },
    }
  )
}

export function getPeriods(entity_id: number) {
  return getLotFilters(Filter.Periods, { entity_id, status: "DECLARATION" })
}
