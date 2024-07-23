import { useMemo } from "react"
import { SafQuery, SafStates } from "saf/types"

export function useSafQuery({
	entity,
	status,
	year,
	search,
	page = 0,
	limit,
	order,
	filters,
	type,
}: SafStates) {
	return useMemo<SafQuery>(
		() => ({
			entity_id: entity.id,
			year,
			status,
			search,
			from_idx: page * (limit ?? 0),
			limit: limit || undefined,
			sort_by: order?.column,
			order: order?.direction,
			type,
			...filters,
		}),
		[entity.id, year, status, search, limit, order, filters, page, type]
	)
}
