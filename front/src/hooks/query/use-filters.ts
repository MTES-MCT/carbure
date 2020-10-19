import { useState } from "react"

import { PageSelection } from "../../components/system/pagination"
import { SelectValue } from "../../components/system/select"
import { Filters } from "../../services/types"

export interface FilterSelection {
  selected: { [k in Filters]?: SelectValue }
  select: (type: Filters, value: SelectValue) => void
  reset: () => void
}

// manage current filter selection
export default function useFilterSelection(
  initialState: FilterSelection["selected"],
  pagination: PageSelection
): FilterSelection {
  const [selected, setFilters] = useState<FilterSelection["selected"]>(
    initialState
  )

  function select(type: Filters, value: SelectValue) {
    pagination.setPage(0)
    setFilters({ ...selected, [type]: value })
  }

  function reset() {
    setFilters(initialState)
  }

  return { selected, select, reset }
}
