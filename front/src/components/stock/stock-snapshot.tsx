import React from "react"

import { ApiState } from "../../hooks/helpers/use-api"
import { LotStatus, StockSnapshot } from "../../services/types"
import { StatusSelection } from "../../hooks/query/use-status"

import styles from "./stock-snapshot.module.css"

import { Title, StatusButton } from "../system"
import { Alert } from "../system/alert"

import { mapStatus } from "../transaction/transaction-snapshot"

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
