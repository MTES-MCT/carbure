import { useState } from "react"

import { PageSelection } from "../../../common/components/pagination"
import { FilterSelection } from "./use-filters"
import { SpecialSelection } from "./use-special"

export interface YearSelection {
  selected: number
  setYear: (y: number) => void
}

export default function useYearSelection(
  pagination: PageSelection,
  filters: FilterSelection,
  special: SpecialSelection
): YearSelection {
  const [selected, setSelected] = useState(new Date().getFullYear())

  function setYear(year: number) {
    pagination.setPage(0)
    filters.reset()
    special.reset()
    setSelected(year)
  }

  return { selected, setYear }
}
