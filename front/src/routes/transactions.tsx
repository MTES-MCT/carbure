import React from "react"

import useTransactions from "../hooks/transactions/use-transactions"

import { Main } from "../components/system"
import { Route, Switch } from "../components/relative-route"
import { TransactionSnapshot } from "../components/transaction-snapshot"
import { TransactionList } from "../components/transaction-list"
import TransactionDetails from "./transaction-details"
import TransactionAdd from "./transaction-add"
import TransactionOutSummary from "./transaction-out-summary"
import TransactionFilters from "../components/transaction-filters"

export const Transactions = () => {
  const {
    entity,
    status,
    filters,
    year,
    invalid,
    deadline,
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
      <TransactionSnapshot snapshot={snapshot} status={status} year={year} />

      <TransactionFilters
        filters={filters}
        search={search}
        options={snapshot.data?.filters}
      />

      <TransactionList
        transactions={transactions}
        status={status}
        sorting={sorting}
        selection={selection}
        pagination={pagination}
        invalid={invalid}
        deadline={deadline}
        uploader={uploader}
        deleter={deleter}
        validator={validator}
        duplicator={duplicator}
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
