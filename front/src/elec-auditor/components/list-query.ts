import { ElecAuditorApplicationsQuery, ElecAuditorApplicationsStates } from "elec-auditor/types"
import { useMemo } from "react"

export function useApplicationsQuery({
  entity,
  year,
  status,
  search,
  page = 0,
  limit,
  order,
  filters,
}: ElecAuditorApplicationsStates) {
  return useMemo<ElecAuditorApplicationsQuery>(
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
