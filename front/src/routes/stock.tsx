import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"

import { useStocks } from "../hooks/use-stock"
import { Main } from "../components/system"
import { StocksSnapshot } from "../components/transaction-snapshot"
import { StockList } from "../components/transaction-list"

export const Stocks = ({ entity }: { entity: EntitySelection }) => {
  const {
    filters,
    pagination,
    snapshot,
    transactions,
    search,
    sorting,
    refresh,
  } = useStocks(entity)

  if (entity === null) {
    return null
  }

  return (
    <Main>
      <StocksSnapshot snapshot={snapshot} filters={filters} search={search} />

      <StockList
        transactions={transactions}
        sorting={sorting}
        pagination={pagination}
      />
    </Main>
  )
}

export default Stocks
