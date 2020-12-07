import React from "react"

import { ApiState } from "common/hooks/helpers/use-api"
import { LotStatus, StockSnapshot } from "common/types"
import { StatusSelection } from "common/hooks/query/use-status"

import styles from "./stock-snapshot.module.css"

import { Title, StatusButton } from "common/components"
import { Alert } from "common/components/alert"

import { mapStatus } from "transactions/components/transaction-snapshot"

const STOCK_STATUSES = [LotStatus.Inbox, LotStatus.Stock, LotStatus.ToSend]

type StockSnapshotProps = {
  snapshot: ApiState<StockSnapshot>
  status: StatusSelection
}

export const StocksSnapshot = ({ snapshot, status }: StockSnapshotProps) => (
  <div className={styles.stockSnapshot}>
    {snapshot.error && <Alert level="error">{snapshot.error}</Alert>}

    {!snapshot.error && (
      <React.Fragment>
        <div className={styles.stockHeader}>
          <Title>Stock</Title>
        </div>

        <div className={styles.stockStatus}>
          {mapStatus(snapshot.data?.lots, STOCK_STATUSES).map(
            ([key, label, amount]) => (
              <StatusButton
                key={key}
                active={key === status.active}
                loading={snapshot.loading}
                amount={amount}
                label={label}
                onClick={() => status.setActive(key)}
              />
            )
          )}
        </div>
      </React.Fragment>
    )}
  </div>
)
