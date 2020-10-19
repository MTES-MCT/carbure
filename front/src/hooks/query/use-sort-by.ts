import { useState } from "react"

export interface SortingSelection {
  column: string
  order: "asc" | "desc"
  sortBy: (c: string) => void
}

export default function useSortingSelection(): SortingSelection {
  const [current, setCurrent] = useState<{
    column: string
    order: "asc" | "desc"
  }>({ column: "", order: "asc" })

  function sortBy(column: string) {
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
