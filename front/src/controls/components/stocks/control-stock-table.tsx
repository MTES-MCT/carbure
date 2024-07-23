import { memo } from "react"
import { Stock } from "transactions/types"
import Table, { Order, selectionColumn } from "common/components/table"
import { useStockColumns } from "transactions/components/stocks/stock-table"
import { To } from "react-router-dom"
import { compact } from "common/utils/collection"

export interface ControlStockTableProps {
	loading: boolean
	stocks: Stock[]
	order: Order | undefined
	selected: number[]
	onSelect: (selected: number[]) => void
	onOrder: (order: Order | undefined) => void
	rowLink: (stock: Stock) => To
}

export const ControlStockTable = memo(
	({
		loading,
		stocks,
		order,
		selected,
		onSelect,
		onOrder,
		rowLink,
	}: ControlStockTableProps) => {
		const columns = useStockColumns()
		return (
			<Table
				loading={loading}
				order={order}
				onOrder={onOrder}
				rowLink={rowLink}
				rows={stocks}
				columns={compact([
					selectionColumn(stocks, selected, onSelect, (s: Stock) => s.id),
					columns.status,
					columns.period,
					columns.quantity,
					columns.feedstock,
					columns.supplier,
					columns.client,
					columns.productionSite,
					columns.depot,
					columns.ghgReduction,
				])}
			/>
		)
	}
)

export default ControlStockTable
