import { api, Api, download } from "common/services/api"
import {
	ElecChargePointsApplication,
	ElecChargePointsApplicationDetails,
} from "elec/types"
import { ElecAuditFilter, ElecAuditQuery, ElecAuditSnapshot } from "./types"
import { ElecChargePointsApplicationsData } from "elec-audit-admin/types"

export function getYears(entity_id: number) {
	return api.get<Api<number[]>>("/elec/audit/years", {
		params: { entity_id },
	})
}
export function getChargePointDetails(
	entity_id: number,
	charge_point_id: number
) {
	return api.get<Api<ElecChargePointsApplication>>(
		"/elec/admin/charge-points/application-details",
		{
			params: { entity_id, charge_point_id },
		}
	)
}

// AUDIT
export function getSnapshot(entity_id: number, year: number) {
	return api.get<Api<ElecAuditSnapshot>>("/elec/audit/snapshot", {
		params: { entity_id, year },
	})
}

//CHARGE POINT
export function getChargePointsApplications(query: ElecAuditQuery) {
	return api.get<Api<ElecChargePointsApplicationsData>>(
		"/elec/audit/applications",
		{
			params: query,
		}
	)
}

const QUERY_RESET: Partial<ElecAuditQuery> = {
	limit: undefined,
	from_idx: undefined,
	sort_by: undefined,
	order: undefined,
}

export async function getElecAuditChargePointsApplicationsFilters(
	field: ElecAuditFilter,
	query: ElecAuditQuery
) {
	const params = { filter: field, ...query, ...QUERY_RESET }
	const result = await api
		.get<Api<string[]>>("/elec/audit/filters", { params })
		.then((res) => res.data.data ?? [])
	return result
}

export function getChargePointsApplicationDetails(
	entityId: number,
	applicationId: number
) {
	return api.get<Api<ElecChargePointsApplicationDetails>>(
		"/elec/audit/application-details",
		{
			params: { entity_id: entityId, application_id: applicationId },
		}
	)
}

export function downloadChargePointsSample(
	entityId: number,
	applicationId: number
) {
	return download("/elec/audit/get-sample", {
		entity_id: entityId,
		application_id: applicationId,
		export: true,
	})
}
