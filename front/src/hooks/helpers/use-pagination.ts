import { useEffect, useState } from "react"

export type PageSelection = {
  page: number
  limit: number
  setPage: (p: number) => void
  setLimit: (l: number) => void
}

// manage pagination state
export function usePageSelection(): PageSelection {
  const [{ page, limit }, setPagination] = useState({ page: 0, limit: 10 })

  useEffect(() => {
    setPage(0)
  }, [limit])

  function setPage(page: number) {
    setPagination({ limit, page })
  }

  function setLimit(limit: number) {
    setPagination({ page, limit })
  }

  return { page, limit, setPage, setLimit }
}
