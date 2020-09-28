import React from "react"

import styles from "./pagination.module.css"

import { ChevronLeft, ChevronRight } from "./system/icons"
import { Button, Select } from "./system"

// generate a list of numbers from 0 to size-1
const list = (size: number) => Array.from(Array(Math.ceil(size)).keys())

type PaginationProps = {
  page: number
  total: number
  limit: number
  onChange: (p: number) => void
}

const Pagination = ({ page, limit, total, onChange }: PaginationProps) => {
  const pages = Math.ceil(total / limit)

  function changePage(index: number) {
    onChange(Math.max(0, Math.min(index, pages - 1)))
  }

  return (
    <div className={styles.pagination}>
      <Button
        className={styles.paginationButton}
        onClick={() => changePage(page - 1)}
      >
        <ChevronLeft />
      </Button>

      <Select
        value={page}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
          changePage(parseInt(e.target.value, 10))
        }
      >
        {list(pages).map((i) => (
          <option key={i} value={i}>
            {i + 1}
          </option>
        ))}
      </Select>

      <span className={styles.paginationTotal}>sur {pages}</span>

      <Button
        className={styles.paginationButton}
        onClick={() => changePage(page + 1)}
      >
        <ChevronRight />
      </Button>
    </div>
  )
}

export default Pagination
