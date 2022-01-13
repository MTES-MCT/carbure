import { StockQuery } from "../../types"
import { ActionBar } from "common-v2/components/scaffold"
import { TransformManyButton } from "transactions/actions/transform"
import { ExportStocksButton } from "transactions/actions/export"
import { StockExcelButton } from "transactions/actions/stock-excel"

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
      <ExportStocksButton {...props} />
    </ActionBar>
  )
}

export default StockActions
