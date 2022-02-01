import { ActionBar } from "common-v2/components/scaffold"
import { SearchInput } from "common-v2/components/input"
import { ExportLotsButton } from "../actions/export"
import { LotQuery } from "transactions/types"
import { PinManyButton } from "controls/actions/pin"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
  search: string | undefined
  onSearch: (search: string | undefined) => void
  onSwitch: (category: string) => void
}

export const ControlActions = ({
  count,
  search,
  onSearch,
  onSwitch,
  ...props
}: ActionBarProps) => {
  return (
    <ActionBar>
      <ExportLotsButton {...props} />
      <PinManyButton {...props} />

      <SearchInput
        asideX
        clear
        debounce={250}
        value={search}
        onChange={onSearch}
      />
    </ActionBar>
  )
}

export default ControlActions
