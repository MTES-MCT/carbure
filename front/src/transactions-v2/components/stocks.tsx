import { useState } from "react"
import { Entity } from "carbure/types"
import { Snapshot } from "../types"
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
  const filters = useFilters()
  const pagination = usePagination()

  const [category, setCategory] = useState("pending")
  const [search, setSearch] = useState<string | undefined>()
  const [selection, setSelection] = useState<number[]>([])

  const query = useStockQuery({
    entity,
    category: category,
    search,
    pagination,
    filters: filters.selected,
  })

  const stocks = useQuery(api.getStocks, {
    key: "stocks",
    params: [query],
  })

  const count = {
    pending: snapshot?.lots.stock ?? 0,
    history: snapshot?.lots.stock_total ?? 0,
  }

  const stocksData = stocks.result?.data.data
  const stockList = stocksData?.stocks ?? []
  const returned = stocksData?.returned ?? 0
  const total = stocksData?.total ?? 0

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
            selected={selection}
            onSelect={setSelection}
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
