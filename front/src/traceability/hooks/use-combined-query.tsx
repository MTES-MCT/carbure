import { useMemo } from "react"
import { ActionQuery } from "traceability/types"

// The query builder always sends `status`, often `undefined`. An undefined key
// must not erase a value already set by the page or the tab.
function withoutUndefined<T extends Partial<ActionQuery>>(query: T): T {
  const defined: T = { ...query }
  for (const key in defined) {
    if (defined[key] === undefined) delete defined[key]
  }
  return defined
}

export function combineQueries<
  Base extends Partial<ActionQuery>,
  Override extends Partial<ActionQuery>,
>(base: Base, override: Override) {
  return { ...withoutUndefined(base), ...withoutUndefined(override) }
}

export function useCombinedQuery<
  Base extends Partial<ActionQuery>,
  Override extends Partial<ActionQuery>,
>(base: Base, override: Override) {
  return useMemo(() => combineQueries(base, override), [base, override])
}
