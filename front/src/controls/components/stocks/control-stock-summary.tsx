import pickApi from "../../api"
import useEntity from "carbure/hooks/entity"
import {
	StockSummaryBar,
	StockSummaryBarProps,
} from "transactions/components/stocks/stock-summary"

export const ControlStockSummaryBar = (props: StockSummaryBarProps) => {
	const entity = useEntity()
	const api = pickApi(entity)

	return <StockSummaryBar {...props} getSummary={api.getStocksSummary} />
}
