import React, { useState } from "react"

import useAPI, { ApiState } from "../hooks/use-api"
import { Settings } from "../services/settings"
import { getSnapshot, getLots, LotStatus } from "../services/lots"

import { Main } from "../components/system"
import TransactionSnapshot from "../components/transaction-snapshot"
import TransactionList from "../components/transaction-list"
import Pagination from "../components/pagination"

// @TODO harcoded pagination limit value
const LIMIT = 10

type TransactionsProps = {
  settings: ApiState<Settings>
  entity: number
}

const Transactions = ({ settings, entity }: TransactionsProps) => {
  const snapshot = useAPI(getSnapshot)
  const transactions = useAPI(getLots)

  const [activeStatus, setActiveStatus] = useState(LotStatus.Drafts)
  const [page, setPage] = useState(0)

  if (entity < 0 || !settings.data) {
    return null
  }

  const right = settings.data.rights.find(
    (right) => right.entity.id === entity
  )!

  snapshot.useResolve(right.entity.id)
  transactions.useResolve(activeStatus, right.entity.id, page, LIMIT)

  return (
    <React.Fragment>
      <TransactionSnapshot
        snapshot={snapshot}
        activeStatus={activeStatus}
        setActiveStatus={setActiveStatus}
      />

      <Main>
        {transactions.data && (
          <TransactionList transactions={transactions.data.lots} />
        )}

        {transactions.data && (
          <Pagination
            from={page}
            limit={LIMIT}
            total={transactions.data.total}
            onChange={setPage}
          />
        )}
      </Main>
    </React.Fragment>
  )
}

export default Transactions
