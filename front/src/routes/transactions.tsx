import React from "react"

import { EntitySelection } from "../hooks/use-app"
import { Settings } from "../services/types"
import { ApiState } from "../hooks/use-api"

import useTransactions from "../hooks/use-transactions"

import { Main } from "../components/system"
import TransactionSnapshot from "../components/transaction-snapshot"
import TransactionList from "../components/transaction-list"
import TransactionDetails from "./transaction-details"
import { Route } from "react-router-dom"

type TransactionsProps = {
  settings: ApiState<Settings>
  entity: EntitySelection
}

const Transactions = ({ settings, entity }: TransactionsProps) => {
  const {
    status,
    filters,
    pagination,
    snapshot,
    transactions,
  } = useTransactions(entity)

  if (entity.selected === null || settings.data === null) {
    return null
  }

  return (
    <Main>
      <TransactionSnapshot
        snapshot={snapshot}
        status={status}
        filters={filters}
      />

      <TransactionList
        transactions={transactions.data}
        pagination={pagination}
      />

      <Route exact path="/transactions/:id">
        <TransactionDetails transactions={transactions.data} />
      </Route>
    </Main>
  )
}

export default Transactions
