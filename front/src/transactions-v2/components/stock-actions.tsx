import { StockQuery } from "../hooks/stock-query"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { Flask } from "common-v2/components/icons"
import { ExportButton } from "transactions-v2/actions"

export interface StockActionsProps {
  count: number
  query: StockQuery
  selection: number[]
}

export const StockActions = ({ count, ...props }: StockActionsProps) => {
  return (
    <ActionBar>
      <Button icon={Flask} variant="primary" label={"Transformer"} />
      <ExportButton {...props} />
    </ActionBar>
  )
}

export default StockActions
