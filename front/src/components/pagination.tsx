import React from "react"

import styles from "./pagination.module.css"

import { ChevronLeft, ChevronRight } from "./system/icons"
import { Button } from "./system"
import Select from "./system/select"

// generate a list of numbers from 0 to size-1
const list = (size: number) =>
  Array.from(Array(Math.ceil(size)).keys()).map((i) => ({
    value: i,
    label: `${i + 1}`,
  }))

type PaginationProps = {
  page: number
  total: number
  limit: number
  onChange: (p: number) => void
}

const Pagination = ({ page, limit, total, onChange }: PaginationProps) => {
  const pageCount = Math.ceil(total / limit)
  const pages = list(pageCount)

  function changePage(index: number) {
    onChange(Math.max(0, Math.min(index, pageCount - 1)))
  }

  return (
    <div className={styles.pagination}>
      <Button
        disabled={page === 0}
        className={styles.paginationButton}
        onClick={() => changePage(page - 1)}
      >
        <ChevronLeft />
      </Button>

      <Select
        value={page}
        options={pages}
        className={styles.paginationSelect}
        onChange={(value) => changePage(value as number)}
      />

      <span className={styles.paginationTotal}>sur {pageCount}</span>

      <Button
        disabled={page === pageCount - 1}
        className={styles.paginationButton}
        onClick={() => changePage(page + 1)}
      >
        <ChevronRight />
      </Button>
    </div>
  )
}

export default Pagination
