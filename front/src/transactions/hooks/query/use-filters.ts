import { useEffect, useState } from "react"
import { useHistory, useLocation } from "react-router-dom"

import { PageSelection } from "common/components/pagination"
import { SelectValue } from "common/components/select"
import { Filters } from "common/types"

function useLocationFilters() {
  const location = useLocation()
  const [filters, setFilters] = useState<FilterSelection["selected"]>({})

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search)
    const queryFilters: FilterSelection["selected"] = {}

    queryParams.forEach((value, filter) => {
      let filterValue: SelectValue = value
        .split(",")
        .map((v) => (v === "true" || v === "false" ? v === "true" : v))

      if (filterValue) {
        queryFilters[filter as Filters] = filterValue
      }
    })

    if (JSON.stringify(queryFilters) !== JSON.stringify(filters)) {
      setFilters(queryFilters)
    }
  }, [location.search, filters])

  return filters
}

export interface FilterSelection {
  selected: { [k in Filters]?: SelectValue }
  select: (type: Filters, value: SelectValue) => void
  reset: () => void
  isFiltered: () => boolean
}

// manage current filter selection
export default function useFilterSelection(
  pagination: PageSelection
): FilterSelection {
  const history = useHistory()
  const location = useLocation()
  const selected = useLocationFilters()

  function select(type: Filters, value: SelectValue) {
    const queryParams = new URLSearchParams(location.search)

    if (Array.isArray(value) && value.length > 0) {
      queryParams.set(type, value.toString())
    } else {
      queryParams.delete(type)
    }

    const queryString = queryParams.toString().replace(/%2C/g, ",")

    if (queryString) {
      pagination.setPage(0)
      history.push(`?${queryString}`)
    } else {
      reset()
    }
  }

  function reset() {
    pagination.setPage(0)
    history.push({ search: "" })
  }

  function isFiltered() {
    return Object.values(selected).some((filter) => {
      if (Array.isArray(filter)) {
        return filter.length > 0
      } else {
        return filter !== null
      }
    })
  }

  return { selected, select, reset, isFiltered }
}
