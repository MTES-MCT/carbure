import { useRef } from "react"
import { equals } from "ramda"

// Callers rebuild query objects on each render. Keep the previous one while
// its values stay the same, so dependent memos do not recompute.
export function useStableQuery<T>(query: T): T {
  const cache = useRef(query)
  if (!equals(cache.current, query)) {
    cache.current = query
  }
  return cache.current
}
