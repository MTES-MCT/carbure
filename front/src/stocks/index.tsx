import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { EntityType, Filters } from "common/types"

import { usePageSelection } from "common/components/pagination"
import useSortingSelection from "common/hooks/query/use-sort-by"
import { useStockStatusSelection } from "common/hooks/query/use-status"
import useSearchSelection from "common/hooks/query/use-search"
import useFilterSelection from "common/hooks/query/use-filters"
import useSpecialSelection from "common/hooks/query/use-special"
import useYearSelection from "common/hooks/query/use-year"
import useTransactionSelection from "common/hooks/query/use-selection"
import useUploadLotFile from "common/hooks/actions/use-upload-file"
import useDuplicateLot from "common/hooks/actions/use-duplicate-lots"
import useDeleteLots from "common/hooks/actions/use-delete-lots"
import useValidateLots from "common/hooks/actions/use-validate-lots"
import useAcceptLots from "common/hooks/actions/use-accept-lots"
import useRejectLots from "common/hooks/actions/use-reject-lots"
import useSendLot from "common/hooks/actions/use-send-lots"
import { useGetStocks, useGetStockSnapshot } from "./hooks/use-stock"

import { Main } from "common/components"

import { Redirect, Route, Switch } from "common/components/relative-route"
import { StocksSnapshot } from "./components/stock-snapshot"
import { StockList } from "./components/stock-list"
import TransactionFilters from "transactions/components/transaction-filters"

import StockDetails from "./routes/stock-details"
import { StockInSummary } from "./routes/stock-in-summary"
import { StockSendComplex } from "./routes/stock-send-complex"

const FILTERS = [
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.CountriesOfOrigin,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

function useStocks(entity: EntitySelection) {
  const pagination = usePageSelection()
  const sorting = useSortingSelection(pagination)
  const status = useStockStatusSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const snapshot = useGetStockSnapshot(entity)
  const special = useSpecialSelection(pagination)
  const year = useYearSelection(pagination, filters, special)
  const stock = useGetStocks(entity, filters, status, pagination, search, sorting) // prettier-ignore

  function refresh() {
    snapshot.getSnapshot()
    stock.getStock()
  }

  const selection = useTransactionSelection(stock.data?.lots)
  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const deleter = useDeleteLots(entity, selection, year, refresh)
  const validator = useValidateLots(entity, selection, year, refresh)
  const acceptor = useAcceptLots(entity, selection, year, refresh)
  const rejector = useRejectLots(entity, selection, year, refresh)
  const sender = useSendLot(entity, selection, refresh)

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
    refresh,
  }
}

export const Stocks = ({ entity }: { entity: EntitySelection }) => {
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
    refresh,
  } = useStocks(entity)

  if (entity === null) {
    return null
  }

  const hasTrading =
    entity.entity_type === EntityType.Trader || entity.has_trading

  if (!hasTrading) {
    return <Redirect to={`/org/${entity.id}`} />
  }

  return (
    <Main>
      <StocksSnapshot snapshot={snapshot} status={status} />

      <TransactionFilters
        search={search}
        selection={filters}
        filters={snapshot.data?.filters}
        placeholder={FILTERS}
      />

      <StockList
        stock={stock}
        sorting={sorting}
        pagination={pagination}
        status={status}
        selection={selection}
        deleter={deleter}
        uploader={uploader}
        validator={validator}
        acceptor={acceptor}
        rejector={rejector}
        duplicator={duplicator}
        sender={sender}
      />

      <Switch>
        <Route relative path="show-summary-in">
          <StockInSummary entity={entity} />
        </Route>

        <Route relative path="send-complex">
          <StockSendComplex entity={entity} />
        </Route>

        <Route relative path=":id">
          <StockDetails
            entity={entity}
            deleter={deleter}
            validator={validator}
            acceptor={acceptor}
            rejector={rejector}
            sender={sender}
            refresh={refresh}
          />
        </Route>
      </Switch>
    </Main>
  )
}

export default Stocks
