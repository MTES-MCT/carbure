import React from "react"
import { ChevronLeft, ChevronRight } from "./icons"

import styles from "./pagination.module.css"
import { Button, Select } from "./system"

// generate a list of numbers from 0 to size-1
const list = (size: number) => Array.from(Array(Math.ceil(size)).keys())

const Pagination = ({ from, limit, total, onChange }: any) => {
  const pages = Math.ceil(total / limit)

  function changePage(index: number) {
    onChange(Math.max(0, Math.min(index, pages - 1)))
  }

  return (
    <div className={styles.pagination}>
      <Button
        className={styles.paginationButton}
        onClick={() => changePage(from - 1)}
      >
        <ChevronLeft />
      </Button>

      <Select
        value={from}
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
        onClick={() => changePage(from + 1)}
      >
        <ChevronRight />
      </Button>
    </div>
  )
}

export default Pagination
