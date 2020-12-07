import { useState } from "react"

import { PageSelection } from "../../system/pagination"

export interface SearchSelection {
  query: string
  setQuery: (s: string) => void
}

// manage search query
export default function useSearchSelection(
  pagination: PageSelection
): SearchSelection {
  const [query, setQueryState] = useState("")

  function setQuery(query: string) {
    pagination.setPage(0)
    setQueryState(query)
  }

  return { query, setQuery }
}
