import React from "react"

import useTransactions from "../hooks/use-transactions"

import { Main } from "../components/system"
import { Route, Switch } from "../components/relative-route"
import TransactionSnapshot from "../components/transaction-snapshot"
import TransactionList from "../components/transaction-list"
import TransactionDetails from "./transaction-details"
import TransactionAdd from "./transaction-add"
import TransactionOutSummary from "./transaction-out-summary"

const Transactions = () => {
  const {
    entity,
    status,
    filters,
    pagination,
    snapshot,
    transactions,
    selection,
    search,
    sorting,
    deleter,
    duplicator,
    validator,
    refresh,
    exportAll,
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
        search={search}
      />

      <TransactionList
        transactions={transactions}
        status={status}
        sorting={sorting}
        selection={selection}
        pagination={pagination}
        onDelete={deleter.resolve}
        onDuplicate={duplicator.resolve}
        onValidate={validator.resolve}
        onExportAll={exportAll}
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

export default Transactions
