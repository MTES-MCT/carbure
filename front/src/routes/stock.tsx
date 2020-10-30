import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"

import { useStocks } from "../hooks/use-stock"
import { Main } from "../components/system"
import { StocksSnapshot } from "../components/transaction-snapshot"
import { StockList } from "../components/transaction-list"
import TransactionFilters from "../components/transaction-filters"

export const Stocks = ({ entity }: { entity: EntitySelection }) => {
  const {
    filters,
    pagination,
    snapshot,
    status,
    stock,
    search,
    sorting,
  } = useStocks(entity)

  if (entity === null) {
    return null
  }

  return (
    <Main>
      <StocksSnapshot 
        snapshot={snapshot}
        status={status} 
      />

      <TransactionFilters
        search={search}
        selection={filters}
        filters={snapshot.data?.filters ?? {}}
      />

      <StockList
        stock={stock}
        sorting={sorting}
        pagination={pagination}
      />

    </Main>
  )
}

export default Stocks
