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
import { ControlStockSummaryBar } from "./control-stock-summary"
import { useLotQuery, useQueryParamsStore } from "transactions/components/lots"
import { Filter, Stock } from "transactions/types"
import ControlStockDetails from "control-details/components/stock"

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
  const stockList = stocksData?.stocks ?? []
  const ids = stocksData?.ids ?? []
  const count = stocksData?.returned ?? 0
  const total = stocksData?.total ?? 0

  const showStockDetails = (stock: Stock) => ({
    pathname: `${stock.id}`,
    search: location.search,
  })

  return (
    <>
      <Bar>
        <Filters
          query={query}
          filters={ADMIN_STOCK_FILTERS}
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
            <ControlStockSummaryBar
              query={query}
              selection={state.selection}
              filters={state.filters}
              onFilter={actions.setFilters}
            />

            <ControlStockTable
              loading={stocks.loading}
              order={state.order}
              stocks={stockList}
              selected={state.selection}
              onSelect={actions.setSelection}
              onOrder={actions.setOrder}
              rowLink={showStockDetails}
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
        <Route path=":id" element={<ControlStockDetails neighbors={ids} />} />
      </Routes>
    </>
  )
}

const ADMIN_STOCK_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.Depots,
]

export default Stocks
