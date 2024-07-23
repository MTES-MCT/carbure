import { ElecAuditQuery, ElecAuditStates } from "elec-audit/types"
import { useMemo } from "react"

export function useElecAuditQuery({
	entity,
	year,
	status,
	search,
	page = 0,
	limit,
	order,
	filters,
}: ElecAuditStates) {
	return useMemo<ElecAuditQuery>(
		() => ({
			entity_id: entity.id,
			year,
			status,
			search,
			from_idx: page * (limit ?? 0),
			limit: limit || undefined,
			sort_by: order?.column,
			order: order?.direction,
			...filters,
		}),
		[entity.id, status, search, limit, order, filters, page, year]
	)
}
