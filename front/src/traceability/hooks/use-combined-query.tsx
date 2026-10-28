import { useMemo } from "react"
import { ActionFilter, ActionQuery } from "traceability/types"

const COMBINABLE_FILTERS = [
  "status",
  ActionFilter.holder,
  ActionFilter.type,
  ActionFilter.material,
  ActionFilter.origin_material,
  ActionFilter.producer,
  ActionFilter.root_pos,
  ActionFilter.nearest_site,
  ActionFilter.shipping_method,
  ActionFilter.site,
] as const

export function useCombinedQuery(
  fixedQuery: Partial<ActionQuery>,
  localQuery: ActionQuery
) {
  return useMemo(() => {
    const combinedFilters = Object.fromEntries(
      COMBINABLE_FILTERS.map((filter) => [
        filter,
        [...(fixedQuery[filter] ?? []), ...(localQuery[filter] ?? [])],
      ])
    )

    return {
      ...fixedQuery,
      ...localQuery,
      ...combinedFilters,
    }
  }, [fixedQuery, localQuery])
}
