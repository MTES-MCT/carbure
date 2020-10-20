import { useState } from "react"

import { PageSelection } from "../../components/system/pagination"
import { FilterSelection } from "./use-filters"
import { InvalidSelection } from "./use-invalid"

export interface YearSelection {
  selected: number
  setYear: (y: number) => void
}

export default function useYearSelection(
  pagination: PageSelection,
  filters: FilterSelection,
  invalid: InvalidSelection
): YearSelection {
  const [selected, setSelected] = useState(new Date().getFullYear())

  function setYear(year: number) {
    pagination.setPage(0)
    filters.reset()
    invalid.setInvalid(false)
    setSelected(year)
  }

  return { selected, setYear }
}
