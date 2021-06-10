import React from "react"
import { Trans } from "react-i18next"

import { ApiState } from "common/hooks/use-api"
import { LotStatus, Snapshot } from "common/types"
import { StatusSelection } from "transactions/hooks/query/use-status"

import { Title } from "common/components"
import { StatusButton } from "common/components/button"
import { Alert } from "common/components/alert"

import { mapStatus } from "transactions/components/list-snapshot"

import styles from "./list-snapshot.module.css"

const STOCK_STATUSES = [LotStatus.Inbox, LotStatus.Stock, LotStatus.ToSend]

type StockSnapshotProps = {
  snapshot: ApiState<Snapshot>
  status: StatusSelection
}

export const StocksSnapshot = ({ snapshot, status }: StockSnapshotProps) => (
  <div className={styles.stockSnapshot}>
    {snapshot.error && <Alert level="error">{snapshot.error}</Alert>}

    {!snapshot.error && (
      <React.Fragment>
        <div className={styles.stockHeader}>
          <Title>
            <Trans>Stock</Trans>
          </Title>
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
