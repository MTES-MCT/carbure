import { useState } from "react"

import { PageSelection } from "../../components/system/pagination"
import { FilterSelection } from "./use-filters"

export interface YearSelection {
  selected: number
  setYear: (y: number) => void
}

export default function useYearSelection(
  pagination: PageSelection,
  filters: FilterSelection
): YearSelection {
  const [selected, setSelected] = useState(new Date().getFullYear())

  function setYear(year: number) {
    pagination.setPage(0)
    filters.reset()
    setSelected(year)
  }

  return { selected, setYear }
}
