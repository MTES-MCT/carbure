import React from "react"

import { EntitySelection } from "../hooks/use-app"
import { Settings } from "../services/types"
import { ApiState } from "../hooks/use-api"

import useTransactions from "../hooks/use-transactions"

import { Main } from "../components/system"
import TransactionSnapshot from "../components/transaction-snapshot"
import TransactionList from "../components/transaction-list"
import Pagination from "../components/pagination"

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

  // boolean for conditional rendering of certain children
  const hasData = transactions.data && transactions.data.total > 0

  return (
    <React.Fragment>
      <TransactionSnapshot
        snapshot={snapshot}
        status={status}
        filters={filters}
      />

      <Main>
        {hasData && <TransactionList transactions={transactions.data!.lots} />}

        {hasData && (
          <Pagination
            page={pagination.selected.page}
            limit={pagination.selected.limit}
            total={transactions.data!.total}
            onChange={pagination.setPage}
          />
        )}

        {!hasData && (
          <span>Aucune transaction trouvée pour ces paramètres.</span>
        )}
      </Main>
    </React.Fragment>
  )
}

export default Transactions
