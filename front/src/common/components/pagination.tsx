import React, { useState } from "react"
import cl from "clsx"

import styles from "./pagination.module.css"

import { ChevronLeft, ChevronRight } from "./icons"
import { Button } from "./button"
import Select from "./select"

// generate a list of numbers from 0 to size-1
const list = (size: number) =>
  Array.from(Array(Math.ceil(size)).keys()).map((i) => ({
    value: i,
    label: `${i + 1}`,
  }))

const limits = [
  { value: 10, label: "10" },
  { value: 25, label: "25" },
  { value: 50, label: "50" },
  { value: 100, label: "100" },
  { value: null, label: "Tous" },
]

export type PageSelection = {
  page: number
  limit: number | null
  setPage: (p: number) => void
  setLimit: (l: number) => void
}

// manage pagination state
export function usePageSelection(): PageSelection {
  const [page, setPage] = useState(0)
  const [limit, setLimitState] = useState<number | null>(10)

  function setLimit(limit: number) {
    setPage(0)
    setLimitState(limit)
  }

  return { page, limit, setPage, setLimit }
}

type PaginationProps = {
  pagination: PageSelection
  total: number
}

const Pagination = ({ pagination, total }: PaginationProps) => {
  const pageCount = pagination.limit ? Math.ceil(total / pagination.limit) : 1
  const pages = list(pageCount)

  return (
    <div className={styles.pagination}>
      <Button
        title="Page précédente"
        disabled={pagination.page === 0}
        className={styles.paginationButton}
        icon={ChevronLeft}
        onClick={() => pagination.setPage(pagination.page - 1)}
      />

      <Select
        above
        value={pagination.page}
        options={pages}
        className={styles.paginationSelect}
        onChange={(value) => pagination.setPage(value as number)}
      />

      <span className={cl(styles.paginationText, styles.paginationTotal)}>
        sur {pageCount},
      </span>

      <Select
        above
        value={pagination.limit}
        options={limits}
        className={styles.paginationSelect}
        onChange={(value) => pagination.setLimit(value as number)}
      />

      <span className={styles.paginationText}>résultats</span>

      <Button
        title="Page suivante"
        disabled={pagination.page === pageCount - 1}
        className={styles.paginationButton}
        icon={ChevronRight}
        onClick={() => pagination.setPage(pagination.page + 1)}
      />
    </div>
  )
}

export default Pagination
