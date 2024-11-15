import { useLocation } from "react-router-dom"
import pickApi from "../../api"
import { EntityManager } from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useStatus } from "../status"
import { Bar } from "common/components/scaffold"
import Pagination from "common/components/pagination"
import NoResult from "common/components/no-result"
import Filters from "transactions/components/filters"
import ControlTable from "./control-lot-table"
import ControlActions from "../control-actions"
import { DeadlineSwitch, InvalidSwitch } from "transactions/components/switches"
import { ControlLotSummaryBar } from "./control-lot-summary"
import { useLotQuery, useQueryParamsStore } from "transactions/components/lots"
import { Filter, Lot } from "transactions/types"
import ControlLotDetails from "control-details/components/lot"
import HashRoute from "common/components/hash-route"

export interface LotsProps {
  entity: EntityManager
  year: number
}

export const Lots = ({ entity, year }: LotsProps) => {
  const location = useLocation()

  const status = useStatus()

  const [state, actions] = useQueryParamsStore(entity, year, status)
  const query = useLotQuery(state)

  const api = pickApi(entity)

  const lots = useQuery(api.getLots, {
    key: "controls",
    params: [query],

    onSuccess: () => {
      if (state.selection.length > 0) {
        actions.setSelection([])
      }
    },
  })

  const lotsData = lots.result?.data
  const lotList = lotsData?.results ?? []
  const ids = lotsData?.ids ?? []
  const lotErrors = lotsData?.errors ?? {}
  const count = lotsData?.results.length ?? 0
  const total = lotsData?.count ?? 0
  const totalErrors = lotsData?.total_errors ?? 0
  const totalDeadline = lotsData?.total_deadline ?? 0

  const showLotDetails = (lot: Lot) => ({
    pathname: location.pathname,
    search: location.search,
    hash: `lot/${lot.id}`,
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
          lots={lotsData?.lots ?? []}
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
            <ControlLotSummaryBar
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
              onOrder={actions.setOrder}
              rowLink={showLotDetails}
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

      <HashRoute
        path="lot/:id"
        element={<ControlLotDetails neighbors={ids} />}
      />
    </>
  )
}

const ADMIN_FILTERS = [
  Filter.LotStatus,
  Filter.CorrectionStatus,
  Filter.DeliveryTypes,
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.Clients,
  Filter.ClientTypes,
  Filter.ProductionSites,
  Filter.DeliverySites,
  Filter.AddedBy,
  Filter.Errors,
  Filter.Conformity,
  Filter.Scores,
  Filter.ML,
]

export default Lots
