import Table, { Column } from "common/components/table"
import { Fragment } from "react"

function groupRowsByYear<T extends { year: number }>(items: T[]) {
	const years: Record<number, T[]> = {}
	items.forEach((item) => {
		years[item.year] = years[item.year] ?? []
		years[item.year].push(item)
	})
	return years
}

type YearTableProps<T> = {
	rows: T[]
	columns: Column<T>[]
	onAction?: (value: T) => void
}

function YearTable<T extends { year: number }>({
	rows,
	columns,
	onAction,
}: YearTableProps<T>) {
	const rowsByYear = groupRowsByYear(rows)

	return (
		<Fragment>
			{Object.entries(rowsByYear).map(([year, yearRows], i) => (
				<Fragment key={year}>
					<h2>{year}</h2>
					<Table
						headless={i > 0}
						columns={columns}
						rows={yearRows}
						onAction={onAction}
					/>
				</Fragment>
			))}
		</Fragment>
	)
}

export default YearTable
