import { useState } from "react"
import { useLocation } from "react-router-dom"

import { PageSelection } from "common/components/pagination"
import { SelectValue } from "common/components/select"
import { Filters, Entity, EntityType } from "common/types"

const defaultState = {}

// useful for admins who want to get directly on a filtered page
// when doing a history.push, you can specify a state
// it will be accessible from history.location.state on the new page
function useLocationStateFilters(
  selected: FilterSelection["selected"],
  select: FilterSelection["select"]
) {
  const { state: loc } = useLocation<{ entity?: Entity; period?: string }>()

  if (!loc) return

  if (loc.entity) {
    const t = loc.entity.entity_type
    const prods = (selected.producers as Array<string>) ?? []
    const traders = (selected.traders as Array<string>) ?? []
    const ops = (selected.operators as Array<string>) ?? []

    if (t === EntityType.Producer && !prods.includes(loc.entity.name)) {
      select(Filters.Producers, [...prods, loc.entity.name])
    } else if (t === EntityType.Trader && !traders.includes(loc.entity.name)) {
      select(Filters.Traders, [...traders, loc.entity.name])
    } else if (t === EntityType.Operator && !ops.includes(loc.entity.name)) {
      select(Filters.Operators, [...ops, loc.entity.name])
    }
  }

  if (loc.period) {
    const periods = (selected.periods as Array<string>) ?? []
    if (!periods.includes(loc.period)) {
      select(Filters.Periods, [...periods, loc.period])
    }
  }
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
  const [selected, setFilters] = useState<FilterSelection["selected"]>(
    defaultState
  )

  function select(type: Filters, value: SelectValue) {
    pagination.setPage(0)
    setFilters({ ...selected, [type]: value })
  }

  function reset() {
    pagination.setPage(0)
    setFilters(defaultState)
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

  useLocationStateFilters(selected, select)

  return { selected, select, reset, isFiltered }
}
