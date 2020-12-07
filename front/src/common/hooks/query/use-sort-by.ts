import { useState } from "react"
import { PageSelection } from "../../components/pagination"

export interface SortingSelection {
  column: string
  order: "asc" | "desc"
  sortBy: (c: string) => void
}

export default function useSortingSelection(
  pagination: PageSelection
): SortingSelection {
  const [current, setCurrent] = useState<{
    column: string
    order: "asc" | "desc"
  }>({ column: "", order: "asc" })

  function sortBy(column: string) {
    pagination.setPage(0)

    if (current.column !== column) {
      return setCurrent({ column, order: "asc" })
    } else if (current.column && current.order === "asc") {
      return setCurrent({ column, order: "desc" })
    } else if (current.column && current.order === "desc") {
      return setCurrent({ column: "", order: "asc" })
    }
  }

  return { ...current, sortBy }
}
