import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { EntityType, Filters, LotStatus } from "common/types"

import { usePageSelection } from "common/components/pagination"
import useSpecialSelection from "./hooks/query/use-special"
import useSortingSelection from "./hooks/query/use-sort-by"
import useSearchSelection from "./hooks/query/use-search"
import useFilterSelection from "./hooks/query/use-filters"
import useStatusSelection from "./hooks/query/use-status"
import useYearSelection from "./hooks/query/use-year"
import useTransactionSelection from "./hooks/query/use-selection"
import useUploadLotFile from "./hooks/actions/use-upload-file"
import useDuplicateLot from "./hooks/actions/use-duplicate-lots"
import useDeleteLots from "./hooks/actions/use-delete-lots"
import useValidateLots from "./hooks/actions/use-validate-lots"
import useAcceptLots from "./hooks/actions/use-accept-lots"
import useRejectLots from "./hooks/actions/use-reject-lots"
import useDeclareLots from "./hooks/actions/use-declare-lots"
import { useGetLots, useGetSnapshot } from "./hooks/use-transaction-list"

import { Main } from "common/components"
import { Redirect, Route, Switch } from "common/components/relative-route"
import { TransactionSnapshot } from "./components/list-snapshot"
import { TransactionList } from "./components/list"
import TransactionFilters from "./components/list-filters"

import TransactionAdd from "./routes/transaction-add"
import TransactionDetails from "./routes/transaction-details"
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

const ADMIN_STATUSES = [
  LotStatus.Alert,
  LotStatus.Correction,
  LotStatus.Declaration,
]

const OPERATOR_FILTERS = [
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.CountriesOfOrigin,
  Filters.Vendors,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

const PRODUCER_TRADER_FILTERS = [
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.CountriesOfOrigin,
  Filters.Clients,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

const ADMIN_FILTERS = [
  Filters.DeliveryStatus,
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.CountriesOfOrigin,
  Filters.Vendors,
  Filters.Clients,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

export function useTransactions(entity: EntitySelection) {
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
  const declarator = useDeclareLots(entity)

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
    declarator,
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
    declarator,
    refresh,
  } = useTransactions(entity)

  if (entity === null) {
    return null
  }

  const isTrader = entity.entity_type === EntityType.Trader
  const isOperator = entity.entity_type === EntityType.Operator
  const isProducer = entity.entity_type === EntityType.Producer
  const isAdmin = entity.entity_type === EntityType.Administration

  if (isAdmin && !ADMIN_STATUSES.includes(status.active)) {
    return <Redirect relative to=".." />
  }

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
    : isAdmin
    ? ADMIN_STATUSES
    : PRODUCER_TRADER_STATUSES

  const filtersPlaceholder = isOperator
    ? OPERATOR_FILTERS
    : isAdmin
    ? ADMIN_FILTERS
    : PRODUCER_TRADER_FILTERS

  return (
    <Main>
      <TransactionSnapshot
        snapshot={snapshot}
        status={status}
        year={year}
        placeholder={statusPlaceholder}
        declarator={isAdmin ? null : declarator}
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
        filters={filters}
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
            transactions={transactions}
          />
        </Route>
      </Switch>
    </Main>
  )
}

export default Transactions
