import { useMemo } from "react"
import { useSearchParams } from "react-router"
import { QueryFilters } from "./query-builder-2.types"
import useLocalStorage from "../storage"

const excludedFilters = ["page", "limit", "order", "search"]
// Get the filters defined in the url to populate the store
export const useFilterSearchParams = () => {
  const [filtersParams, setFiltersParams] = useSearchParams()
  const filters = useMemo(() => {
    const filters: QueryFilters = {}
    filtersParams.forEach((value, filter) => {
      if (excludedFilters.includes(filter)) return
      filters[filter] = filters[filter] ?? []
      filters[filter]!.push(value)
    })
    return filters
  }, [filtersParams])

  return [filters, setFiltersParams] as const
}

/**
 * Define the number of items per page
 */
export const useLimit = () => {
  return useLocalStorage<number | undefined>("carbure:limit", 10)
}

export const usePage = () => {
  const [searchParams] = useSearchParams()
  const searchParamsPage = searchParams.get("page")

  return searchParamsPage ? parseInt(searchParamsPage) : 1
}
