import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Entity } from "carbure/types"
import { Snapshot, Stock } from "../types"
import { Order } from "common-v2/components/table"
import { useQuery } from "common-v2/hooks/async"
import useStockQuery from "../hooks/stock-query"
import { Bar } from "common-v2/components/scaffold"
import Pagination, { usePagination } from "common-v2/components/pagination"
import Filters, { useFilters } from "../components/filters"
import StockTable from "../components/stock-table"
import NoResult from "../components/no-result"
import StockActions from "../components/stock-actions"
import * as api from "../api"
import { SearchBar } from "./search-bar"

export interface StocksProps {
  entity: Entity
  snapshot: Snapshot | undefined
}

export const Stocks = ({ entity, snapshot }: StocksProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const filters = useFilters()
  const pagination = usePagination()

  const [category, setCategory] = useState("pending")
  const [search, setSearch] = useState<string | undefined>()
  const [selection, setSelection] = useState<number[]>([])
  const [order, setOrder] = useState<Order | undefined>()

  // go back to the first page when the query changes
  const { resetPage } = pagination
  useEffect(() => resetPage(), [filters.selected, category, search, resetPage])

  const query = useStockQuery({
    entity,
    category: category,
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
  const returned = stocksData?.returned ?? 0
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

        <StockActions count={returned} query={query} selection={selection} />

        {returned === 0 && (
          <NoResult
            loading={stocks.loading}
            count={filters.count}
            onReset={filters.resetFilters}
          />
        )}

        {returned > 0 && (
          <StockTable
            loading={stocks.loading}
            stocks={stockList}
            order={order}
            selected={selection}
            onSelect={setSelection}
            onAction={showStockDetails}
            onOrder={setOrder}
          />
        )}

        <Pagination
          page={pagination.page}
          limit={pagination.limit}
          total={total}
          onPage={pagination.setPage}
          onLimit={pagination.setLimit}
        />
      </section>
    </>
  )
}

export default Stocks
