import { Option } from "common/components/select"
import { useCallback, useState } from "react"

import { PageSelection } from "../../../common/components/pagination"
import { FilterSelection } from "./use-filters"
import { SpecialSelection } from "./use-special"

export interface YearSelection {
  selected: number
  setYear: (y: number) => void
  checkYears: (years: Option[]) => void
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

  const checkYears = useCallback(
    (years: Option[]) => {
      // if the currently selected year is not in the list of available years
      // set it to the first available value
      if (!years.some((option) => option.value === selected)) {
        setSelected(years[0].value as number)
      }
    },
    [selected]
  )

  return { selected, setYear, checkYears }
}
