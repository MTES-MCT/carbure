import { useEffect, useState } from "react"

export type PageSelection = {
  page: number
  limit: number
  setPage: (p: number) => void
  setLimit: (l: number) => void
}

// manage pagination state
export function usePageSelection(): PageSelection {
  const [page, setPage] = useState(0)
  const [limit, setLimit] = useState(10)

  useEffect(() => {
    setPage(0)
  }, [limit])

  return { page, limit, setPage, setLimit }
}
