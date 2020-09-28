import React from "react"

import { EntitySelection } from "../hooks/use-app"
import { Settings } from "../services/types"
import { ApiState } from "../hooks/use-api"

import useTransactions from "../hooks/use-transactions"

import { Main } from "../components/system"
import TransactionSnapshot from "../components/transaction-snapshot"
import TransactionList from "../components/transaction-list"

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

  if (entity === null || !settings.data) {
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
        transactions={transactions.data!}
        pagination={pagination}
      />
    </Main>
  )
}

export default Transactions
