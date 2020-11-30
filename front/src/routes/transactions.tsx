import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"

import useTransactions from "../hooks/use-transactions"

import { Main } from "../components/system"
import { Redirect, Route, Switch } from "../components/relative-route"
import { TransactionSnapshot } from "../components/transaction/transaction-snapshot"
import { TransactionList } from "../components/transaction/transaction-list"
import TransactionFilters from "../components/transaction/transaction-filters"

import TransactionDetails from "./transaction/transaction-details"
import TransactionAdd from "./transaction/transaction-add"
import TransactionOutSummary from "./transaction/transaction-out-summary"
import TransactionInSummary from "./transaction/transaction-in-summary"
import { EntityType, LotStatus } from "../services/types"

// prettier-ignore
const OPERATOR_STATUSES = [
  LotStatus.Draft,
  LotStatus.Inbox,
  LotStatus.Accepted,
]

const PRODUCTOR_TRADER_STATUSES = [
  LotStatus.Draft,
  LotStatus.Validated,
  LotStatus.ToFix,
  LotStatus.Accepted,
]

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
    !PRODUCTOR_TRADER_STATUSES.includes(status.active)
  ) {
    return <Redirect relative to=".." />
  }

  const statusPlaceholder = isOperator
    ? OPERATOR_STATUSES
    : PRODUCTOR_TRADER_STATUSES

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
        filters={snapshot.data?.filters ?? {}}
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
