import { useMemo } from "react"
import { Route, Routes, useLocation, useNavigate } from "react-router-dom"
import { Entity } from "carbure/types"
import { Snapshot, Stock, StockQuery, Filter } from "../../types"
import { useQuery } from "common-v2/hooks/async"
import * as api from "../../api"
import { Bar } from "common-v2/components/scaffold"
import Pagination from "common-v2/components/pagination"
import Filters from "../filters"
import StockTable from "./stock-table"
import NoResult from "../no-result"
import StockActions from "./stock-actions"
import { SearchBar } from "../search-bar"
import { StockSummaryBar } from "./stock-summary"
import StockDetails from "stock-details"
import { QueryParams, useQueryParamsStore } from "../lots"

export interface StocksProps {
  entity: Entity
  year: number
  snapshot: Snapshot | undefined
}

const EMPTY: number[] = []

export const Stocks = ({ entity, year, snapshot }: StocksProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const [state, actions] = useQueryParamsStore(entity, year, "stocks", snapshot)
  const query = useStockQuery(state)

  const stocks = useQuery(api.getStocks, {
    key: "stocks",
    params: [query],

    onSuccess: () => {
      if (state.selection.length > 0) {
        actions.setSelection([])
      }
    },
  })

  const stocksData = stocks.result?.data.data
  const stockList = stocksData?.stocks ?? []
  const ids = stocksData?.ids ?? EMPTY
  const count = stocksData?.returned ?? 0
  const total = stocksData?.total ?? 0

  const showStockDetails = (stock: Stock) =>
    navigate({
      pathname: `${stock.id}`,
      search: location.search,
    })

  return (
    <>
      <Bar>
        <Filters
          query={query}
          filters={STOCK_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilters={api.getStockFilters}
        />
      </Bar>

      <section>
        <SearchBar
          count={snapshot?.lots}
          search={state.search}
          category={state.category}
          onSearch={actions.setSearch}
          onSwitch={actions.setCategory}
        />

        <StockActions
          count={count}
          query={query}
          selection={state.selection} //
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

            <StockTable
              loading={stocks.loading}
              stocks={stockList}
              order={state.order}
              selected={state.selection}
              onSelect={actions.setSelection}
              onOrder={actions.setOrder}
              onAction={showStockDetails}
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
        <Route path=":id" element={<StockDetails neighbors={ids} />} />
      </Routes>
    </>
  )
}

const STOCK_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.ProductionSites,
  Filter.Depots,
]

export function useStockQuery({
  entity,
  year,
  category,
  filters,
  search,
  order,
  page,
  limit,
}: QueryParams) {
  return useMemo<StockQuery>(
    () => ({
      entity_id: entity.id,
      year,
      history: category === "history" ? true : undefined,
      query: search ? search : undefined,
      sort_by: order?.column,
      order: order?.direction,
      from_idx: page * (limit ?? 0),
      limit,
      ...filters,
    }),
    [entity.id, year, category, filters, search, order, page, limit]
  )
}

export default Stocks
