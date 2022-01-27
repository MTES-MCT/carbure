import { Snapshot } from "../types"
import { useStatus } from "./status"
import { SearchInput } from "common-v2/components/input"
import { ActionBar } from "common-v2/components/scaffold"
import {
  DraftsSwitcher,
  InputSwitcher,
  OutputSwitcher,
  StockSwitcher,
} from "./category"

export interface SearchBarProps {
  category: string
  search: string | undefined
  count: Snapshot["lots"] | undefined
  onSearch: (search: string | undefined) => void
  onSwitch: (category: string) => void
}

export const SearchBar = ({ search, onSearch, ...props }: SearchBarProps) => {
  const status = useStatus()
  return (
    <ActionBar>
      {status === "drafts" && <DraftsSwitcher {...props} />}
      {status === "in" && <InputSwitcher {...props} />}
      {status === "stocks" && <StockSwitcher {...props} />}
      {status === "out" && <OutputSwitcher {...props} />}

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

export default SearchBar
