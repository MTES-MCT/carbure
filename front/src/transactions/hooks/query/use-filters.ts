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
    const entity = loc.entity.name
    const type = loc.entity.entity_type

    const isVendor = [EntityType.Producer, EntityType.Trader].includes(type)
    const isClient = type === EntityType.Operator

    const vendors = (selected.vendors as Array<string>) ?? []
    const clients = (selected.clients as Array<string>) ?? []

    if (isVendor && !vendors.includes(entity)) {
      select(Filters.Vendors, [...vendors, entity])
    }

    if (isClient && !clients.includes(entity)) {
      select(Filters.Clients, [...clients, entity])
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
