import api, { Api } from "common/services/api"
import { getLotFilters } from "controls/api/admin"
import { Filter } from "transactions/types"
import { DashboardDeclaration } from "./types"

export function getDeclarations(period: string) {
	return api.get<Api<DashboardDeclaration[]>>(
		"transactions/admin/declarations",
		{
			params: { period },
		}
	)
}

export function getPeriods(entity_id: number) {
	return getLotFilters(Filter.Periods, { entity_id, status: "DECLARATIONS" })
}
