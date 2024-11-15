import { useLocation } from "react-router-dom"
import pickApi from "../../api"
import { EntityManager } from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useStatus } from "../status"
import { Bar } from "common/components/scaffold"
import Pagination from "common/components/pagination"
import NoResult from "common/components/no-result"
import Filters from "transactions/components/filters"
import ControlActions from "../control-actions"
import ControlStockTable from "./control-stock-table"
import { ControlStockSummaryBar } from "./control-stock-summary"
import { useLotQuery, useQueryParamsStore } from "transactions/components/lots"
import { Filter, Stock } from "transactions/types"
import ControlStockDetails from "control-details/components/stock"
import HashRoute from "common/components/hash-route"

export interface StocksProps {
  entity: EntityManager
  year: number
}

export const Stocks = ({ entity, year }: StocksProps) => {
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

  const stocksData = stocks.result?.data
  const stockList = stocksData?.results ?? []
  const ids = stocksData?.ids ?? []
  const count = stocksData?.results?.length ?? 0
  const total = stocksData?.count ?? 0

  const showStockDetails = (stock: Stock) => ({
    pathname: location.pathname,
    search: location.search,
    hash: `stock/${stock.id}`,
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

      <HashRoute
        path="stock/:id"
        element={<ControlStockDetails neighbors={ids} />}
      />
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
