import { ActionBar } from "common/components/scaffold"
import { SearchInput } from "common/components/input"
import { ExportLotsButton } from "../actions/export"
import { Lot, LotQuery } from "transactions/types"
import { AlertManyButton } from "controls/actions/alert"
import DeliveryMapButton from "controls/actions/delivery-map"
import useEntity from "carbure/hooks/entity"
import { useStatus } from "./status"
import { SetManyConformityButton } from "controls/actions/set-conformity"
import UpdateManyButton from "controls/actions/update-many"
import { DeleteManyButton } from "controls/actions/delete-many"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection?: number[]
  lots?: Lot[]
  search: string | undefined
  onSearch: (search: string | undefined) => void
  onSwitch: (category: string) => void
}

export const ControlActions = ({
  search,
  lots,
  query,
  selection,
  onSearch,
}: ActionBarProps) => {
  const entity = useEntity()
  const status = useStatus()

  const selectedLots = lots?.filter((lot) => selection?.includes(lot.id))
  const props = { query, selection: selection ?? [] }

  return (
    <ActionBar>
      {status !== "stocks" && (
        <>
          {selectedLots && <AlertManyButton {...props} lots={selectedLots} />}
          {entity.isAdmin && selectedLots && (
            <UpdateManyButton {...props} lots={selectedLots} />
          )}
          {entity.isAdmin && selectedLots && (
            <DeleteManyButton {...props} lots={selectedLots} />
          )}
          {entity.isAdmin && <DeliveryMapButton {...props} />}
          {entity.isAuditor && status === "alerts" && (
            <SetManyConformityButton {...props} />
          )}
        </>
      )}

      <SearchInput
        asideX
        clear
        debounce={250}
        value={search}
        onChange={onSearch}
      />

      <ExportLotsButton {...props} />
    </ActionBar>
  )
}

export default ControlActions
