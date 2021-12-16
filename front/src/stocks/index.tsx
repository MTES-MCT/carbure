import { Route, Routes, Navigate } from "react-router-dom"

import { Entity } from "carbure/types"
import { EntityType, Filters } from "common/types"

import { usePageSelection } from "common/components/pagination"
import useSortingSelection from "transactions/hooks/query/use-sort-by"
import { useStockStatusSelection } from "transactions/hooks/query/use-status"
import useSearchSelection from "transactions/hooks/query/use-search"
import useFilterSelection from "transactions/hooks/query/use-filters"
import useSpecialSelection from "transactions/hooks/query/use-special"
import useYearSelection from "transactions/hooks/query/use-year"
import useTransactionSelection from "transactions/hooks/query/use-selection"
import useUploadLotFile from "transactions/hooks/actions/use-upload-file"
import useDuplicateLot from "transactions/hooks/actions/use-duplicate-lots"
import useDeleteLots from "transactions/hooks/actions/use-delete-lots"
import useValidateLots from "transactions/hooks/actions/use-validate-lots"
import useAcceptLots from "transactions/hooks/actions/use-accept-lots"
import useRejectLots from "transactions/hooks/actions/use-reject-lots"
import useSendLot from "stocks/hooks/use-send-lots"
import { useGetStocks, useGetStockSnapshot } from "./hooks/use-stock-list"

import { Main } from "common/components"

import { StocksSnapshot } from "./components/list-snapshot"
import { StockList } from "./components/list"
import TransactionFilters from "transactions/components/list-filters"

import StockDetails from "./routes/stock-details"
import StockSendComplex from "./routes/stock-send-complex"
import useTransactionQuery from "transactions/hooks/query/use-transaction-query"
import { useSummary } from "transactions/components/summary"

const FILTERS = [
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.CountriesOfOrigin,
  Filters.ProductionSites,
  Filters.Vendors,
  Filters.DeliverySites,
  Filters.ShowEmpty,
]

function useStocks(entity: Entity) {
  const pagination = usePageSelection()
  const sorting = useSortingSelection(pagination)
  const status = useStockStatusSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const snapshot = useGetStockSnapshot(entity)
  const special = useSpecialSelection(pagination)
  const year = useYearSelection(pagination, filters, special)

  const query = useTransactionQuery(
    status.active,
    entity?.id ?? -1,
    filters.selected,
    year.selected,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
    special.invalid,
    special.deadline
  )

  const stock = useGetStocks(query)
  const selection = useTransactionSelection(stock.data?.lots)

  const summary = useSummary(query, selection.selected, {
    stock: true,
    short: true,
  })

  function refresh() {
    snapshot.getSnapshot()
    stock.getStock()
  }

  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const deleter = useDeleteLots(entity, selection, query, refresh, true)
  const validator = useValidateLots(entity, selection, query, refresh, true) // prettier-ignore
  const acceptor = useAcceptLots(entity, selection, query, refresh, true)
  const rejector = useRejectLots(entity, selection, query, refresh, true)
  const sender = useSendLot(entity, selection, query, refresh)

  return {
    filters,
    pagination,
    snapshot,
    status,
    stock,
    search,
    sorting,
    selection,
    uploader,
    duplicator,
    deleter,
    validator,
    acceptor,
    rejector,
    sender,
    summary,
    query,
    refresh,
  }
}

export const Stocks = ({ entity }: { entity: Entity }) => {
  const {
    filters,
    pagination,
    snapshot,
    status,
    stock,
    search,
    sorting,
    selection,
    uploader,
    duplicator,
    deleter,
    validator,
    acceptor,
    rejector,
    sender,
    summary,
    query,
    refresh,
  } = useStocks(entity)

  if (entity === null) {
    return null
  }

  const hasTrading =
    entity.entity_type === EntityType.Trader || entity.has_trading

  if (!hasTrading) {
    return <Navigate to={`/org/${entity.id}`} />
  }

  return (
    <Main>
      <StocksSnapshot snapshot={snapshot} status={status} />

      <TransactionFilters
        stock
        query={query}
        selection={filters}
        filters={snapshot.data?.filters}
        placeholder={FILTERS}
        entity={entity}
      />

      <StockList
        stock={stock}
        sorting={sorting}
        pagination={pagination}
        search={search}
        filters={filters}
        status={status}
        selection={selection}
        deleter={deleter}
        uploader={uploader}
        validator={validator}
        acceptor={acceptor}
        rejector={rejector}
        duplicator={duplicator}
        sender={sender}
        summary={summary}
        query={query}
        entity={entity}
      />

      <Routes>
        <Route
          path="send-complex"
          element={<StockSendComplex entity={entity} />}
        />

        <Route
          path=":id"
          element={
            <StockDetails
              entity={entity}
              deleter={deleter}
              validator={validator}
              acceptor={acceptor}
              rejector={rejector}
              sender={sender}
              refresh={refresh}
              transactions={summary.data?.tx_ids ?? []}
            />
          }
        />
      </Routes>
    </Main>
  )
}

export default Stocks
