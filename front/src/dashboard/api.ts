import api, { Api } from "common-v2/services/api"
import { getLotFilters } from "controls/api/admin"
import { Filter } from "transactions/types"
import { DashboardDeclaration } from "./types"

export function getDeclarations(period: string) {
  return api.get<Api<DashboardDeclaration[]>>("/admin/dashboard/declarations", {
    params: { period },
  })
}

export function getPeriods(entity_id: number) {
  return getLotFilters(Filter.Periods, { entity_id, status: "DECLARATIONS" })
}
