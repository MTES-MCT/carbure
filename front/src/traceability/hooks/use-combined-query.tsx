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

// Later queries override earlier ones. A lone query is kept as given.
type MergedQueries<T extends readonly Partial<ActionQuery>[]> =
  T extends readonly [infer Head, ...infer Tail]
    ? Tail extends readonly [Partial<ActionQuery>, ...Partial<ActionQuery>[]]
      ? Omit<Head, keyof MergedQueries<Tail>> & MergedQueries<Tail>
      : Head
    : Partial<ActionQuery>

export function useCombinedQuery<T extends Partial<ActionQuery>[]>(
  ...queries: T
): MergedQueries<T> {
  return useMemo(
    () =>
      queries.reduce<Partial<ActionQuery>>(
        (combined, query) => ({ ...combined, ...withoutUndefined(query) }),
        {}
      ),
    // The rest array is new every render; React compares each query object.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    queries
  ) as MergedQueries<T>
}
