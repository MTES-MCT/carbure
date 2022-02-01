import { ActionBar } from "common-v2/components/scaffold"
import { SearchInput } from "common-v2/components/input"
import { ExportLotsButton } from "../actions/export"
import { Lot, LotQuery } from "transactions/types"
import { PinManyButton } from "controls/actions/pin"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
  lots: Lot[]
  search: string | undefined
  onSearch: (search: string | undefined) => void
  onSwitch: (category: string) => void
}

export const ControlActions = ({
  count,
  search,
  lots,
  onSearch,
  onSwitch,
  ...props
}: ActionBarProps) => {
  const selectedLots = lots.filter((lot) => props.selection.includes(lot.id))

  return (
    <ActionBar>
      <ExportLotsButton {...props} />
      <PinManyButton {...props} lots={selectedLots} />

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
