import { StockQuery } from "../../types"
import { ActionBar } from "common-v2/components/scaffold"
import { TransformManyButton } from "transactions/actions/transform"
import { ExportStocksButton } from "transactions/actions/export"
import { StockExcelButton } from "transactions/actions/stock-excel"
// import { FlushManyButton } from "transactions/actions/flush-stock"

export interface StockActionsProps {
  count: number
  query: StockQuery
  selection: number[]
}

export const StockActions = ({ count, ...props }: StockActionsProps) => {
  return (
    <ActionBar>
      <StockExcelButton />
      <TransformManyButton {...props} />
      {/* <FlushManyButton {...props} /> */}
      <ExportStocksButton asideX {...props} />
    </ActionBar>
  )
}

export default StockActions
