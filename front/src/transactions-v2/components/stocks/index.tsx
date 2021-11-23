import { useEffect, useMemo, useState } from "react"
import { Route, Routes, useLocation, useNavigate } from "react-router-dom"
import { Entity } from "carbure/types"
import { Snapshot, Stock, FilterSelection, StockQuery } from "../../types"
import { Order } from "common-v2/components/table"
import { PaginationManager } from "common-v2/components/pagination"
import { useQuery } from "common-v2/hooks/async"
import * as api from "../../api"
import { Bar } from "common-v2/components/scaffold"
import Pagination, { usePagination } from "common-v2/components/pagination"
import Filters, { useFilters } from "../filters"
import StockTable from "./stock-table"
import NoResult from "../no-result"
import StockActions from "./stock-actions"
import { SearchBar } from "../search-bar"
import { StockSummaryBar } from "./stock-summary"
import StockDetails from "stock-details"

export interface StocksProps {
  entity: Entity
  snapshot: Snapshot | undefined
}

const EMPTY: number[] = []

export const Stocks = ({ entity, snapshot }: StocksProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const filters = useFilters()
  const pagination = usePagination()

  const [category, setCategory] = useState("pending")
  const [search, setSearch] = useState<string | undefined>()
  const [selection, setSelection] = useState<number[]>(EMPTY)
  const [order, setOrder] = useState<Order | undefined>()

  // go back to the first page and empty selection when the query changes
  const { limit, setPage } = pagination
  useEffect(() => {
    setPage(0)
    setSelection(EMPTY)
  }, [filters.selected, category, search, limit, setPage])

  const query = useStockQuery({
    entity,
    category,
    search,
    pagination,
    order,
    filters: filters.selected,
  })

  const stocks = useQuery(api.getStocks, {
    key: "stocks",
    params: [query],
  })

  const stocksData = stocks.result?.data.data
  const stockList = stocksData?.stocks ?? []
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
          selected={filters.selected}
          onSelect={filters.onFilter}
        />
      </Bar>

      <section>
        <SearchBar
          count={snapshot?.lots}
          search={search}
          category={category}
          onSearch={setSearch}
          onSwitch={setCategory}
        />

        <StockActions count={count} query={query} selection={selection} />

        {count === 0 && <NoResult loading={stocks.loading} filters={filters} />}

        {count > 0 && (
          <>
            <StockSummaryBar
              query={query}
              selection={selection}
              filters={filters}
            />

            <StockTable
              loading={stocks.loading}
              stocks={stockList}
              order={order}
              selected={selection}
              onSelect={setSelection}
              onAction={showStockDetails}
              onOrder={setOrder}
            />

            <Pagination
              page={pagination.page}
              limit={pagination.limit}
              total={total}
              onPage={pagination.setPage}
              onLimit={pagination.setLimit}
            />
          </>
        )}
      </section>

      <Routes>
        <Route path=":id" element={<StockDetails />} />
      </Routes>
    </>
  )
}

export interface StockQueryParams {
  entity: Entity
  category: string
  search: string | undefined
  pagination: PaginationManager
  order: Order | undefined
  filters: FilterSelection
}

export function useStockQuery({
  entity,
  category,
  search,
  pagination,
  order,
  filters,
}: StockQueryParams) {
  const { page = 0, limit } = pagination

  return useMemo<StockQuery>(
    () => ({
      entity_id: entity.id,
      history: category === "history" ? true : undefined,
      query: search ? search : undefined,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    }),
    [entity.id, category, search, page, limit, order, filters]
  )
}

export default Stocks
