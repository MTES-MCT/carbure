import { StockQuery } from "../../types"
import { ActionBar } from "common-v2/components/scaffold"
import { ExportButton } from "transactions-v2/actions"
import { TransformManyButton } from "transactions-v2/actions/transform"

export interface StockActionsProps {
  count: number
  query: StockQuery
  selection: number[]
}

export const StockActions = ({ count, ...props }: StockActionsProps) => {
  return (
    <ActionBar>
      <TransformManyButton {...props} />
      <ExportButton {...props} />
    </ActionBar>
  )
}

export default StockActions
