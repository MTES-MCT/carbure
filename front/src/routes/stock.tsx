import React from "react"

import { useStocks } from "../hooks/use-stock"

import { Main } from "../components/system"
import { StocksSnapshot } from "../components/transaction-snapshot"
import { StockList } from "../components/transaction-list"

export const Stocks = () => {
  const {
   entity,
   filters,
   pagination,
   snapshot,
   transactions,
   search,
   sorting,
   refresh,
 } = useStocks()

 if (entity === null) {
   return null
 }

 return (
   <Main>
     <StocksSnapshot
       snapshot={snapshot}
       filters={filters}
       search={search}
     />

     <StockList
       transactions={transactions}
       sorting={sorting}
       pagination={pagination}
     />
   </Main>
 )
}

export default Stocks
