import React from "react"
import cl from "clsx"

import { Box, SystemProps } from "."
import styles from "./table.module.css"
import { ChevronRight, IconProps } from "./icons"

type LineProps = { text: string; small?: boolean; level?: "warning" }

export const Line = ({ text, small = false, level }: LineProps) => (
  <span
    title={text}
    className={cl(
      styles.rowLine,
      small && styles.extraInfo,
      level === "warning" && styles.lineWarning
    )}
  >
    {small ? text : text || "N/A"}
  </span>
)

type TwoLinesProps = { text: string; sub: string }

export const TwoLines = ({ text, sub }: TwoLinesProps) => (
  <div className={styles.dualRow}>
    <Line text={text} />
    <Line small text={sub} />
  </div>
)

export const arrow: Column<any> = {
  className: styles.actionColumn,
  render: () => (
    <Box className={styles.actionCell}>
      <ChevronRight />
    </Box>
  ),
}

interface Action<T> {
  icon: React.ComponentType<IconProps>
  title: string
  action: (i: T) => void
}

export function Actions<T>(
  config: Action<T>[] | ((c: T) => Action<T>[])
): Column<T> {
  return {
    className: styles.actionColumn,

    render: (cell) => (
      <Box className={styles.actionCell}>
        <ChevronRight className={styles.actionArrow} />

        <Box row className={styles.actionList}>
          {/* if config is a function, create actions dynamically */}
          {(typeof config === "function" ? config(cell) : config).map(
            ({ icon: Icon, title, action }, i) => (
              <Icon
                key={i}
                title={title}
                onClick={(e) => {
                  e.stopPropagation()
                  action(cell)
                }}
              />
            )
          )}
        </Box>
      </Box>
    ),
  }
}

export interface Column<T> {
  /** element displayed in table header */
  header?: React.ReactNode
  /** key by which this column should sort */
  sortBy?: string
  /**  a class for the `<th>` element */
  className?: string
  /** how to render a cell based on the row data */
  render: (row: T) => React.ReactNode
}

export interface Row<T> {
  /** class of the `<tr>` element  */
  className?: string
  /** callback when user clicks on row  */
  onClick?: () => void
  /** raw data for this row  */
  value: T
}

type TableProps<T> = SystemProps & {
  rows: Row<T>[]
  columns: Column<T>[]
  sortBy?: string
  order?: "asc" | "desc"
  onSort?: (s: string) => void
}

export default function Table<T>({
  rows,
  columns,
  sortBy,
  order,
  className,
  onSort,
  ...props
}: TableProps<T>) {
  return (
    <Box {...props} className={cl(styles.table, className)}>
      <Box row>
        {columns.map((column, c) => (
          <Box
            row
            key={c}
            className={cl(styles.tableHeader, column.className)}
            onClick={() => column.sortBy && onSort && onSort(column.sortBy)}
          >
            {column.header ?? null}
            {sortBy && sortBy === column.sortBy && (
              <span>{order === "asc" ? " ▲" : " ▼"}</span>
            )}
          </Box>
        ))}
      </Box>

      {rows.map((row, r) => (
        <Box
          row
          key={r}
          className={cl(styles.tableRow, row.className)}
          onClick={row.onClick}
        >
          {columns.map((column, c) => (
            <Box row key={c} className={cl(styles.tableCell, column.className)}>
              {column.render(row.value)}
            </Box>
          ))}
        </Box>
      ))}
    </Box>
  )
}
