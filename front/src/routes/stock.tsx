import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"

import { useStocks } from "../hooks/use-stock"
import { Main } from "../components/system"
import { StocksSnapshot } from "../components/transaction-snapshot"
import { StockList } from "../components/transaction-list"
import TransactionFilters from "../components/transaction-filters"
import { Route, Switch } from "../components/relative-route"
import { StockInSummary } from "./stock-in-summary"
import { StockSendComplex } from "./stock-send-complex"

export const Stocks = ({ entity }: { entity: EntitySelection }) => {
  const {
    filters,
    pagination,
    snapshot,
    status,
    stock,
    search,
    sorting,
    selection,
    uploader,
    duplicator,
    deleter,
    validator,
    acceptor,
    rejector,  
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
        status={status}
        selection={selection}
        deleter={deleter}
        uploader={uploader}
        validator={validator}
        acceptor={acceptor}
        rejector={rejector}
        duplicator={duplicator}
      />

      <Switch>
        <Route relative path="show-summary-in">
          <StockInSummary entity={entity} />
        </Route>
        <Route relative path="send-complex">
          <StockSendComplex entity={entity} />
        </Route>        
      </Switch>
    </Main>
  )
}

export default Stocks
