import { useMemo } from "react"
import { Route, Routes, useLocation, useNavigate } from "react-router-dom"
import { Entity } from "carbure/types"
import { Snapshot, Stock, FilterSelection, StockQuery } from "../../types"
import { Order } from "common-v2/components/table"
import { useQuery } from "common-v2/hooks/async"
import * as api from "../../api"
import { Bar } from "common-v2/components/scaffold"
import Pagination, { useLimit } from "common-v2/components/pagination"
import Filters, { useFilterParams } from "../filters"
import StockTable from "./stock-table"
import NoResult from "../no-result"
import StockActions from "./stock-actions"
import { SearchBar } from "../search-bar"
import { StockSummaryBar } from "./stock-summary"
import StockDetails from "stock-details"
import useStore from "common-v2/hooks/store"

export interface StocksProps {
  entity: Entity
  year: number
  snapshot: Snapshot | undefined
}

const EMPTY: number[] = []

export const Stocks = ({ entity, year, snapshot }: StocksProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const [state, actions] = useStockQueryStore(entity, year)
  const query = useStockQuery(state)

  const stocks = useQuery(api.getStocks, {
    key: "stocks",
    params: [query],
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
          status="stocks"
          query={query}
          filters={state.filters}
          onFilter={actions.setFilters}
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

export interface StockQueryState {
  entity: Entity
  year: number
  category: string
  filters: FilterSelection
  search: string | undefined
  selection: number[]
  page: number
  limit: number | undefined
  order: Order | undefined
}

function useStockQueryStore(entity: Entity, year: number) {
  const [limit, saveLimit] = useLimit()
  const [filtersParams, setFiltersParams] = useFilterParams()

  const [state, actions] = useStore(
    {
      entity,
      year,
      category: "pending",
      filters: filtersParams,
      search: undefined,
      order: undefined,
      selection: [],
      page: 0,
      limit,
    } as StockQueryState,
    {
      setEntity: (entity: Entity) => ({
        entity,
        category: "pending",
        filters: {},
        search: "",
        selection: [],
        page: 0,
      }),

      setYear: (year: number) => ({
        year,
        category: "pending",
        filters: {},
        search: "",
        selection: [],
        page: 0,
      }),

      setCategory: (category: string) => ({
        category,
        filters: {},
        search: "",
        selection: [],
        page: 0,
      }),

      setFilters: (filters: FilterSelection) => {
        setFiltersParams(filters)
        return {
          filters,
          search: "",
          selection: [],
          page: 0,
        }
      },

      setSearch: (search: string | undefined) => ({
        search,
        selection: [],
        page: 0,
      }),

      setOrder: (order: Order | undefined) => ({
        order,
      }),

      setSelection: (selection: number[]) => ({
        selection,
      }),

      setPage: (page: number) => ({
        page,
        selection: [],
      }),

      setLimit: (limit: number | undefined) => {
        saveLimit(limit)
        return {
          limit,
          selection: [],
          page: 0,
        }
      },
    }
  )

  // sync state with entity defined above
  if (state.entity.id !== entity.id) {
    actions.setEntity(entity)
  }

  // sync state with year defined above
  if (state.year !== year) {
    actions.setYear(year)
  }

  return [state, actions] as [typeof state, typeof actions]
}

export function useStockQuery({
  entity,
  year,
  category,
  filters,
  search,
  order,
  page,
  limit,
}: StockQueryState) {
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
