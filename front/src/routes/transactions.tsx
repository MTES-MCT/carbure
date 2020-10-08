import React from "react"
import { Route, Switch } from "react-router-dom"

import { EntitySelection } from "../hooks/use-app"

import useTransactions from "../hooks/use-transactions"

import { Main } from "../components/system"
import TransactionSnapshot from "../components/transaction-snapshot"
import TransactionList from "../components/transaction-list"
import TransactionDetails from "./transaction-details"
import TransactionAdd from "./transaction-add"

type TransactionsProps = {
  entity: EntitySelection
}

const Transactions = ({ entity }: TransactionsProps) => {
  const {
    status,
    filters,
    pagination,
    snapshot,
    transactions,
    selection,
    deleter,
    duplicator,
    validator,
    refresh,
    search,
  } = useTransactions(entity)

  if (entity.selected === null) {
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
        selection={selection}
        pagination={pagination}
        onDelete={deleter.resolve}
        onDuplicate={duplicator.resolve}
        onValidate={validator.resolve}
      />

      <Switch>
        <Route path="/transactions/add">
          <TransactionAdd entity={entity} refresh={refresh} />
        </Route>

        <Route exact path="/transactions/:id">
          <TransactionDetails
            entity={entity}
            transactions={transactions.data}
            refresh={refresh}
          />
        </Route>
      </Switch>
    </Main>
  )
}

export default Transactions
