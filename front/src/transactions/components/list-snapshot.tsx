import React from "react"
import { useTranslation, TFunction, Trans } from "react-i18next"

import { LotStatus, Snapshot } from "common/types"
import { ApiState } from "common/hooks/use-api"
import { StatusSelection } from "transactions/hooks/query/use-status"
import { YearSelection } from "transactions/hooks/query/use-year"

import { Title } from "common/components"
import { Button, StatusButton } from "common/components/button"
import Select from "common/components/select"
import { Alert } from "common/components/alert"

import styles from "./list-snapshot.module.css"
import { Certificate } from "common/components/icons"
import { LotDeclarator } from "transactions/hooks/actions/use-declare-lots"

const STATUS_ORDER = [
  LotStatus.Draft,
  LotStatus.Alert,
  LotStatus.Validated,
  LotStatus.Inbox,
  LotStatus.ToFix,
  LotStatus.Correction,
  LotStatus.Stock,
  LotStatus.Accepted,
  LotStatus.Weird,
  LotStatus.ToSend,
  LotStatus.Declaration,
  LotStatus.Highlight,
]

export function mapStatus(
  statuses: { [key: string]: number } | undefined,
  placeholder: LotStatus[],
  t: TFunction<"translation">
): [LotStatus, string, number][] {
  const statusList: [string, number][] =
    typeof statuses === "undefined"
      ? placeholder.map((s) => [s, 0])
      : Object.entries(statuses)

  statusList.sort(
    (a, b) =>
      STATUS_ORDER.indexOf(a[0] as LotStatus) -
      STATUS_ORDER.indexOf(b[0] as LotStatus)
  )

  const STATUS_LABEL = {
    [LotStatus.Draft]: (count: number) => t("Brouillon", { count }),
    [LotStatus.Validated]: (count: number) => t("Lot envoyé", { count }),
    [LotStatus.ToFix]: (count: number) => t("Lot en correction", { count }),
    [LotStatus.Accepted]: (count: number) => t("Lot accepté", { count }),
    [LotStatus.Weird]: (count: number) => t("Lot incohérent", { count }),
    [LotStatus.Inbox]: (count: number) => t("Lot reçu", { count }),
    [LotStatus.Stock]: (count: number) => t("Lot en stock", { count }),
    [LotStatus.ToSend]: (count: number) => t("Lot à envoyer", { count }),
    [LotStatus.Alert]: (count: number) => t("Alerte", { count }),
    [LotStatus.Correction]: (count: number) => t("Correction", { count }),
    [LotStatus.Declaration]: (count: number) => t("Lot déclaré", { count }),
    [LotStatus.Highlight]: (count: number) => t("Lot épinglé", { count }),
  }

  return statusList.map(([key, amount = 0]) => {
    const status = key as LotStatus
    const label = STATUS_LABEL[status]
    return [status, label(amount), amount]
  })
}

type TransactionSnapshotProps = {
  placeholder: LotStatus[]
  snapshot: ApiState<Snapshot>
  status: StatusSelection
  year: YearSelection
  declarator: LotDeclarator | null
}

export const TransactionSnapshot = ({
  placeholder,
  snapshot,
  status,
  year,
  declarator,
}: TransactionSnapshotProps) => {
  const { t } = useTranslation()

  return (
    <div className={styles.transactionSnapshot}>
      {snapshot.error && <Alert level="error">{snapshot.error}</Alert>}

      {!snapshot.error && (
        <React.Fragment>
          <div className={styles.transactionHeader}>
            <Title>
              <Trans>Transactions</Trans>
            </Title>

            <Select
              level="inline"
              className={styles.transactionYear}
              value={year.selected}
              placeholder={snapshot.loading ? "…" : t("Choisir une année")}
              options={snapshot.data?.years ?? []}
              onChange={(value) => year.setYear(value as number)}
            />

            {declarator && (
              <Button
                icon={Certificate}
                level="primary"
                className={styles.transactionDeclaration}
                onClick={declarator.confirmDeclaration}
              >
                <Trans>Valider ma déclaration</Trans>
              </Button>
            )}
          </div>

          <div className={styles.transactionStatus}>
            {mapStatus(snapshot.data?.lots, placeholder, t).map(
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
}

export default TransactionSnapshot
