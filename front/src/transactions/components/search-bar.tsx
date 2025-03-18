import { LotQuery, Snapshot } from "../types"
import { useStatus } from "./status"
import { SearchInput } from "common/components/input"
import { ActionBar } from "common/components/scaffold"
import {
  DraftsSwitcher,
  InputSwitcher,
  OutputSwitcher,
  StockSwitcher,
} from "./category"
import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"
import {
  ExportLotsButton,
  ExportStocksButton,
} from "transactions/actions/export"

export interface SearchBarProps {
  category: string
  search: string | undefined
  count: Snapshot["lots"] | undefined
  query: LotQuery
  selection: number[]
  onSearch: (search: string | undefined) => void
  onSwitch: (category: string) => void
}

export const SearchBar = ({
  search,
  onSearch,
  query,
  selection,
  ...props
}: SearchBarProps) => {
  const entity = useEntity()
  const status = useStatus()

  const isReadOnly = !entity.hasRights(UserRole.Admin, UserRole.ReadWrite)

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
      {isReadOnly &&
        (status === "stocks" ? (
          <ExportStocksButton query={query} selection={selection} />
        ) : (
          <ExportLotsButton query={query} selection={selection} />
        ))}
    </ActionBar>
  )
}

export default SearchBar
