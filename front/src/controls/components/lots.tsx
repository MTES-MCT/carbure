import { Route, Routes, useNavigate, useLocation } from "react-router-dom"
import * as api from "../api"
import { Entity } from "carbure/types"
import { useQuery } from "common-v2/hooks/async"
import { useStatus } from "./status"
import { Bar } from "common-v2/components/scaffold"
import Pagination from "common-v2/components/pagination"
import NoResult from "transactions/components/no-result"
import Filters from "transactions/components/filters"
import ControlTable from "./control-table"
import ControlActions from "./control-actions"
import { DeadlineSwitch, InvalidSwitch } from "transactions/components/switches"
import { LotSummaryBar } from "./control-summary"
import { useLotQuery, useQueryParamsStore } from "transactions/components/lots"
import { Filter, Lot } from "transactions/types"
import ControlDetails from "control-details"

export interface LotsProps {
  entity: Entity
  year: number
}

export const Lots = ({ entity, year }: LotsProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const status = useStatus()

  const [state, actions] = useQueryParamsStore(entity, year, status)
  const query = useLotQuery(state)

  const lots = useQuery(api.getLots, {
    key: "controls",
    params: [query],

    onSuccess: () => {
      if (state.selection.length > 0) {
        actions.setSelection([])
      }
    },
  })

  const lotsData = lots.result?.data.data
  const lotList = lotsData?.lots ?? []
  const ids = lotsData?.ids ?? []
  const lotErrors = lotsData?.errors ?? {}
  const count = lotsData?.returned ?? 0
  const total = lotsData?.total ?? 0
  const totalErrors = lotsData?.total_errors ?? 0
  const totalDeadline = lotsData?.total_deadline ?? 0

  const showLotDetails = (lot: Lot) =>
    navigate({
      pathname: `${status}/${lot.id}`,
      search: location.search,
    })

  return (
    <>
      <Bar>
        <Filters
          query={query}
          filters={ADMIN_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilters={api.getLotFilters}
        />
      </Bar>

      <section>
        <ControlActions
          count={count}
          query={query}
          selection={state.selection}
          search={state.search}
          onSearch={actions.setSearch}
          onSwitch={actions.setCategory}
        />

        {(state.invalid || totalErrors > 0) && (
          <InvalidSwitch
            count={totalErrors}
            active={state.invalid}
            onSwitch={actions.setInvalid}
          />
        )}

        {(state.deadline || totalDeadline > 0) && (
          <DeadlineSwitch
            count={totalDeadline}
            active={state.deadline}
            onSwitch={actions.setDeadline}
          />
        )}

        {count === 0 && (
          <NoResult
            loading={lots.loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}

        {count > 0 && (
          <>
            <LotSummaryBar
              query={query}
              selection={state.selection}
              filters={state.filters}
              onFilter={actions.setFilters}
            />

            <ControlTable
              loading={lots.loading}
              order={state.order}
              lots={lotList}
              errors={lotErrors}
              selected={state.selection}
              onSelect={actions.setSelection}
              onAction={showLotDetails}
              onOrder={actions.setOrder}
            />

            <Pagination
              page={state.page}
              limit={state.limit}
              total={total}
              onPage={actions.setPage}
              onLimit={actions.setLimit}
            />
          </>
        )}
      </section>

      <Routes>
        <Route
          path=":status/:id"
          element={<ControlDetails neighbors={ids} />}
        />
      </Routes>
    </>
  )
}

const ADMIN_FILTERS = [
  Filter.Mac,
  Filter.DeliveryStatus,
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
  Filter.AddedBy,
  Filter.Forwarded,
  Filter.Errors,
  Filter.HiddenByAdmin,
  Filter.ClientTypes,
]

export default Lots
