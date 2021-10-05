import { DialogSubtitle } from "common/components/dialog"
import Table, { Column, Row } from "common/components/table"
import { Fragment } from "react"

function groupRowsByYear<T extends { year: number }>(items: Row<T>[]) {
  const years: Record<number, Row<T>[]> = {}
  items.forEach((item) => {
    years[item.value.year] = years[item.value.year] ?? []
    years[item.value.year].push(item)
  })
  return years
}

type YearTableProps<T> = {
  rows: Row<T>[]
  columns: Column<T>[]
}

function YearTable<T extends { year: number }>({
  rows,
  columns,
}: YearTableProps<T>) {
  const rowsByYear = groupRowsByYear(rows)

  return (
    <Fragment>
      {Object.entries(rowsByYear).map(([year, yearRows], i) => {
        return (
          <Fragment key={year}>
            <DialogSubtitle>{year}</DialogSubtitle>
            <Table headless={i > 0} columns={columns} rows={yearRows} />
          </Fragment>
        )
      })}
    </Fragment>
  )
}

export default YearTable
