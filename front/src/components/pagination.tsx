import React from "react"
import cl from "clsx"

import { PageSelection } from "../hooks/helpers/use-pagination"

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

const limits = [
  { value: 10, label: "10" },
  { value: 25, label: "25" },
  { value: 50, label: "50" },
  { value: 100, label: "100" },
]

type PaginationProps = {
  pagination: PageSelection
  total: number
}

const Pagination = ({ pagination, total }: PaginationProps) => {
  const pageCount = Math.ceil(total / pagination.limit)
  const pages = list(pageCount)

  return (
    <div className={styles.pagination}>
      <Button
        disabled={pagination.page === 0}
        className={styles.paginationButton}
        onClick={() => pagination.setPage(pagination.page - 1)}
      >
        <ChevronLeft />
      </Button>

      <Select
        value={pagination.page}
        options={pages}
        className={styles.paginationSelect}
        onChange={(value) => pagination.setPage(value as number)}
      />

      <span className={cl(styles.paginationText, styles.paginationTotal)}>
        sur {pageCount},
      </span>

      <Select
        value={pagination.limit}
        options={limits}
        className={styles.paginationSelect}
        onChange={(value) => pagination.setLimit(value as number)}
      />

      <span className={styles.paginationText}>résultats</span>

      <Button
        disabled={pagination.page === pageCount - 1}
        className={styles.paginationButton}
        onClick={() => pagination.setPage(pagination.page + 1)}
      >
        <ChevronRight />
      </Button>
    </div>
  )
}

export default Pagination
