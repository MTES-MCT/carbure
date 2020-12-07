import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { EntityType, Filters, LotStatus } from "common/types"

import { usePageSelection } from "common/system/pagination"
import useSpecialSelection from "common/hooks/query/use-special"
import useSortingSelection from "common/hooks/query/use-sort-by"
import useSearchSelection from "common/hooks/query/use-search"
import useFilterSelection from "common/hooks/query/use-filters"
import useStatusSelection from "common/hooks/query/use-status"
import useYearSelection from "common/hooks/query/use-year"
import useTransactionSelection from "common/hooks/query/use-selection"
import useUploadLotFile from "common/hooks/actions/use-upload-file"
import useDuplicateLot from "common/hooks/actions/use-duplicate-lots"
import useDeleteLots from "common/hooks/actions/use-delete-lots"
import useValidateLots from "common/hooks/actions/use-validate-lots"
import useAcceptLots from "common/hooks/actions/use-accept-lots"
import useRejectLots from "common/hooks/actions/use-reject-lots"
import { useGetLots, useGetSnapshot } from "./hooks/use-transactions"

import { Main } from "common/system"
import { Redirect, Route, Switch } from "common/components/relative-route"
import { TransactionSnapshot } from "./components/transaction-snapshot"
import { TransactionList } from "./components/transaction-list"
import TransactionFilters from "./components/transaction-filters"

import TransactionAdd from "./routes/transaction-add"
import TransactionDetails from "./routes/transaction-details"
import TransactionOutSummary from "./routes/transaction-out-summary"
import TransactionInSummary from "./routes/transaction-in-summary"

// prettier-ignore
const OPERATOR_STATUSES = [
  LotStatus.Draft,
  LotStatus.Inbox,
  LotStatus.Accepted,
]

const PRODUCER_TRADER_STATUSES = [
  LotStatus.Draft,
  LotStatus.Validated,
  LotStatus.ToFix,
  LotStatus.Accepted,
]

const OPERATOR_FILTERS = [
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.Vendors,
  Filters.CountriesOfOrigin,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

const PRODUCER_TRADER_FILTERS = [
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.Clients,
  Filters.CountriesOfOrigin,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

function useTransactions(entity: EntitySelection) {
  const pagination = usePageSelection()

  const special = useSpecialSelection(pagination)
  const sorting = useSortingSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const status = useStatusSelection(pagination, special)
  const year = useYearSelection(pagination, filters, special)

  const snapshot = useGetSnapshot(entity, year)
  const transactions = useGetLots(entity, status, filters, year, pagination, search, sorting, special) // prettier-ignore

  function refresh() {
    snapshot.getSnapshot()
    transactions.getTransactions()
  }

  const selection = useTransactionSelection(transactions.data?.lots)

  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const deleter = useDeleteLots(entity, selection, year, refresh)
  const validator = useValidateLots(entity, selection, year, refresh)
  const acceptor = useAcceptLots(entity, selection, year, refresh)
  const rejector = useRejectLots(entity, selection, year, refresh)

  return {
    entity,
    status,
    filters,
    year,
    pagination,
    snapshot,
    transactions,
    selection,
    search,
    special,
    sorting,
    deleter,
    uploader,
    duplicator,
    validator,
    acceptor,
    rejector,
    refresh,
  }
}

export const Transactions = ({ entity }: { entity: EntitySelection }) => {
  const {
    status,
    filters,
    year,
    special,
    pagination,
    snapshot,
    transactions,
    selection,
    search,
    sorting,
    deleter,
    duplicator,
    validator,
    uploader,
    acceptor,
    rejector,
    refresh,
  } = useTransactions(entity)

  if (entity === null) {
    return null
  }

  const isTrader = entity.entity_type === EntityType.Trader
  const isOperator = entity.entity_type === EntityType.Operator
  const isProducer = entity.entity_type === EntityType.Producer

  if (isOperator && !OPERATOR_STATUSES.includes(status.active)) {
    return <Redirect relative to=".." />
  }

  if (
    (isProducer || isTrader) &&
    !PRODUCER_TRADER_STATUSES.includes(status.active)
  ) {
    return <Redirect relative to=".." />
  }

  const statusPlaceholder = isOperator
    ? OPERATOR_STATUSES
    : PRODUCER_TRADER_STATUSES

  const filtersPlaceholder = isOperator
    ? OPERATOR_FILTERS
    : PRODUCER_TRADER_FILTERS

  return (
    <Main>
      <TransactionSnapshot
        snapshot={snapshot}
        status={status}
        year={year}
        placeholder={statusPlaceholder}
      />

      <TransactionFilters
        search={search}
        selection={filters}
        filters={snapshot.data?.filters}
        placeholder={filtersPlaceholder}
      />

      <TransactionList
        entity={entity}
        transactions={transactions}
        status={status}
        sorting={sorting}
        selection={selection}
        pagination={pagination}
        special={special}
        uploader={uploader}
        deleter={deleter}
        validator={validator}
        duplicator={duplicator}
        acceptor={acceptor}
        rejector={rejector}
      />

      <Switch>
        <Route relative path="add">
          <TransactionAdd entity={entity} refresh={refresh} />
        </Route>

        <Route relative path="show-summary-out">
          <TransactionOutSummary entity={entity} />
        </Route>

        <Route relative path="show-summary-in">
          <TransactionInSummary entity={entity} />
        </Route>

        <Route relative path=":id">
          <TransactionDetails
            entity={entity}
            refresh={refresh}
            deleter={deleter}
            validator={validator}
            acceptor={acceptor}
            rejector={rejector}
          />
        </Route>
      </Switch>
    </Main>
  )
}

export default Transactions
