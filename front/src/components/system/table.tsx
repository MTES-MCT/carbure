import React from "react"
import cl from "clsx"

import { Box, SystemProps } from "."

import styles from "./table.module.css"
import { ChevronRight, IconProps } from "./icons"

type LineProps = { text: string; small?: boolean }

export const Line = ({ text, small = false }: LineProps) => (
  <span title={text} className={cl(styles.rowLine, small && styles.extraInfo)}>
    {text}
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

export function Actions<T>(actions: Action<T>[]): Column<T> {
  return {
    className: styles.actionColumn,

    render: (cell) => (
      <Box className={styles.actionCell}>
        <ChevronRight className={styles.actionArrow} />

        <Box row className={styles.actionList}>
          {actions.map(({ icon: Icon, title, action }, i) => (
            <Icon
              key={i}
              title={title}
              onClick={(e) => {
                e.stopPropagation()
                action(cell)
              }}
            />
          ))}
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
    <table {...props} className={cl(styles.table, className)}>
      <thead>
        <tr>
          {columns.map((column, c) => (
            <th
              key={c}
              className={column.className}
              onClick={() => column.sortBy && onSort && onSort(column.sortBy)}
            >
              {column.header ?? null}
              {sortBy && sortBy === column.sortBy && (
                <span>{order === "asc" ? " ▲" : " ▼"}</span>
              )}
            </th>
          ))}
        </tr>
      </thead>

      <tbody>
        {rows.map((row, r) => (
          <tr key={r} className={row.className} onClick={row.onClick}>
            {columns.map((column, c) => (
              <td key={c} className={column.className}>
                {column.render(row.value)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
