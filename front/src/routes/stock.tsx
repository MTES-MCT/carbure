import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"
import { EntityType, Filters } from "../services/types"

import { useStocks } from "../hooks/use-stock"
import { Main } from "../components/system"
import { StocksSnapshot } from "../components/stock/stock-snapshot"
import { StockList } from "../components/stock/stock-list"
import TransactionFilters from "../components/transaction/transaction-filters"

const FILTERS = [
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.CountriesOfOrigin,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

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
    sender,
  } = useStocks(entity)

  if (entity === null) {
    return null
  }

  const hasTrading =
    entity.entity_type === EntityType.Trader || entity.has_trading

  if (!hasTrading) {
    return <Redirect to={`/org/${entity.id}`} />
  }

  return (
    <Main>
      <StocksSnapshot snapshot={snapshot} status={status} />

      <TransactionFilters
        search={search}
        selection={filters}
        filters={snapshot.data?.filters}
        placeholder={FILTERS}
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
        sender={sender}
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
