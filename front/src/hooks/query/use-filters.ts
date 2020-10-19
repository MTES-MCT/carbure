import { useState } from "react"

import { PageSelection } from "../../components/system/pagination"
import { SelectValue } from "../../components/system/select"
import { Filters } from "../../services/types"

export interface FilterSelection {
  selected: { [k in Filters]: SelectValue }
  select: (type: Filters, value: SelectValue) => void
  reset: () => void
}

// manage current filter selection
export default function useFilterSelection(
  pagination: PageSelection
): FilterSelection {
  const [selected, setFilters] = useState<FilterSelection["selected"]>({
    [Filters.Biocarburants]: null,
    [Filters.MatieresPremieres]: null,
    [Filters.CountriesOfOrigin]: null,
    [Filters.Periods]: null,
    [Filters.Clients]: null,
    [Filters.ProductionSites]: null,
    [Filters.DeliverySites]: null,
  })

  function select(type: Filters, value: SelectValue) {
    pagination.setPage(0)
    setFilters({ ...selected, [type]: value })
  }

  function reset() {
    setFilters({
      [Filters.Biocarburants]: null,
      [Filters.MatieresPremieres]: null,
      [Filters.CountriesOfOrigin]: null,
      [Filters.Periods]: null,
      [Filters.Clients]: null,
      [Filters.ProductionSites]: null,
      [Filters.DeliverySites]: null,
    })
  }

  return { selected, select, reset }
}
