import React from "react"

import useTransactions from "../hooks/use-transactions"

import { Main } from "../components/system"
import { Route, Switch } from "../components/relative-route"
import { TransactionSnapshot, StockSnapshot } from "../components/transaction-snapshot"
import TransactionList from "../components/transaction-list"
import TransactionDetails from "./transaction-details"
import TransactionAdd from "./transaction-add"
import TransactionOutSummary from "./transaction-out-summary"

export const Transactions = () => {
  const {
    entity,
    status,
    filters,
    year,
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
    refresh,
  } = useTransactions()

  if (entity === null) {
    return null
  }

  return (
    <Main>
      <TransactionSnapshot
        snapshot={snapshot}
        status={status}
        filters={filters}
        year={year}
        search={search}
      />

      <TransactionList
        transactions={transactions}
        status={status}
        sorting={sorting}
        selection={selection}
        pagination={pagination}
        uploader={uploader}
        deleter={deleter}
        validator={validator}
        onDuplicate={duplicator.resolve}
        onExportAll={transactions.exportAll}
      />

      <Switch>
        <Route relative path="add">
          <TransactionAdd entity={entity} refresh={refresh} />
        </Route>

        <Route relative path="show-summary-out">
          <TransactionOutSummary entity={entity} />
        </Route>

        <Route relative path=":id">
          <TransactionDetails
            entity={entity}
            transactions={transactions}
            refresh={refresh}
          />
        </Route>
      </Switch>
    </Main>
  )
}

export const Stocks = () => {
   const {
    entity,
    status,
    filters,
    year,
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
    refresh,
  } = useTransactions()

  if (entity === null) {
    return null
  }

  return (
    <Main>
      <StockSnapshot
        snapshot={snapshot}
        status={status}
        filters={filters}
        year={year}
        search={search}
      />

      <TransactionList
        transactions={transactions}
        status={status}
        sorting={sorting}
        selection={selection}
        pagination={pagination}
        uploader={uploader}
        deleter={deleter}
        validator={validator}
        onDuplicate={duplicator.resolve}
        onExportAll={transactions.exportAll}
      />
    </Main>
  )
}

export default Transactions
