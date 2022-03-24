import { Route, Routes, useNavigate, useLocation } from "react-router-dom"
import pickApi from "../../api"
import { EntityManager } from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import { useStatus } from "../status"
import { Bar } from "common-v2/components/scaffold"
import Pagination from "common-v2/components/pagination"
import NoResult from "transactions/components/no-result"
import Filters from "transactions/components/filters"
import ControlActions from "../control-actions"
import ControlStockTable from "./control-stock-table"
import { StockSummaryBar } from "./control-stock-summary"
import { useLotQuery, useQueryParamsStore } from "transactions/components/lots"
import { Filter, Stock } from "transactions/types"
import ControlDetails from "control-details"

export interface StocksProps {
  entity: EntityManager
  year: number
}

export const Stocks = ({ entity, year }: StocksProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const status = useStatus()

  const [state, actions] = useQueryParamsStore(entity, year, status)
  const query = useLotQuery(state)

  const api = pickApi(entity)

  const stocks = useQuery(api.getStocks, {
    key: "controls",
    params: [query],

    onSuccess: () => {
      if (state.selection.length > 0) {
        actions.setSelection([])
      }
    },
  })

  const stocksData = stocks.result?.data.data
  const lotList = stocksData?.stocks ?? []
  const ids = stocksData?.ids ?? []
  const count = stocksData?.returned ?? 0
  const total = stocksData?.total ?? 0

  const showStockDetails = (stock: Stock) =>
    navigate({
      pathname: `stocks/${stock.id}`,
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
          getFilters={api.getStockFilters}
        />
      </Bar>

      <section>
        <ControlActions
          count={count}
          query={query}
          search={state.search}
          onSearch={actions.setSearch}
          onSwitch={actions.setCategory}
        />

        {count === 0 && (
          <NoResult
            loading={stocks.loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}

        {count > 0 && (
          <>
            <StockSummaryBar
              query={query}
              selection={state.selection}
              filters={state.filters}
              onFilter={actions.setFilters}
            />

            <ControlStockTable
              loading={stocks.loading}
              order={state.order}
              stocks={lotList}
              selected={state.selection}
              onSelect={actions.setSelection}
              onAction={showStockDetails}
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
  Filter.LotStatus,
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
]

export default Stocks
