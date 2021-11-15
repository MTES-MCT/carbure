import { StockQuery } from "../hooks/stock-query"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { SearchInput } from "common-v2/components/input"
import { HistorySwitcher } from "./switches"
import { Flask } from "common-v2/components/icons"

export interface StockActionsProps {
  count: number
  query: StockQuery
  selection: number[]
  pending: number
  history: number
  category: string
  search: string | undefined
  onSwitch: (tab: string) => void
  onSearch: (search: string | undefined) => void
}

export const StockActions = ({
  count,
  category,
  pending,
  history,
  search,
  onSwitch,
  onSearch,
  ...props
}: StockActionsProps) => {
  return (
    <ActionBar>
      <HistorySwitcher
        focus={category}
        pending={pending}
        history={history}
        onFocus={onSwitch}
      />

      <Button
        icon={Flask}
        variant="primary"
        label={"Transformer"}
      />

      <SearchInput
        clear
        asideX
        debounce={240}
        value={search}
        onChange={onSearch}
      />
    </ActionBar>
  )
}

export default StockActions