import { Fragment, useEffect } from "react"
import { Trans, useTranslation } from "react-i18next"
import Table, { Column, Line } from "common/components/table"
import { EntityType, SummaryItem, TransactionQuery } from "common/types"
import { padding } from "./list-columns"
import { AlertCircle, Check, Return } from "common/components/icons"

import { Box, LoaderOverlay, Title } from "common/components"
import styles from "./summary.module.css"
import colStyles from "./list-columns.module.css"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import useAPI from "common/hooks/use-api"
import { Button } from "common/components/button"
import { prettyVolume } from "transactions/helpers"
import { Alert } from "common/components/alert"
import { EntitySelection } from "carbure/hooks/use-entity"
import { getStocksSummary } from "stocks/api"
import {
  getLotsSummary,
  getAuditorSummary,
  getAdminSummary,
} from "transactions/api"

type TransactionSummaryProps = {
  in?: SummaryItem[] | null
  out?: SummaryItem[] | null
  transactions?: SummaryItem[] | null
}

const TransactionSummary = (props: TransactionSummaryProps) => {
  const { t } = useTranslation()

  const summaryInRows = (props.in ?? []).map((v) => ({ value: v }))
  const summaryOutRows = (props.out ?? []).map((v) => ({ value: v }))
  const summaryAllRows = (props.transactions ?? []).map((v) => ({ value: v }))

  const isInEmpty = summaryInRows.length === 0
  const isOutEmpty = summaryOutRows.length === 0
  const isAllEmpty = summaryAllRows.length === 0

  const totalIn = {
    volume: summaryInRows.reduce((t, r) => t + r.value.volume, 0),
    lots: summaryInRows.reduce((t, r) => t + r.value.lots, 0),
  }

  const totalOut = {
    volume: summaryOutRows.reduce((t, r) => t + r.value.volume, 0),
    lots: summaryOutRows.reduce((t, r) => t + r.value.lots, 0),
  }

  const totalAll = {
    volume: summaryAllRows.reduce((t, r) => t + r.value.volume, 0),
    lots: summaryAllRows.reduce((t, r) => t + r.value.lots, 0),
  }

  const columns: Column<SummaryItem>[] = [
    {
      header: t("Biocarburant"),
      render: (d) => <Line text={t(d.biocarburant, { ns: "biofuels" })} />,
    },
    {
      header: t("Volume (litres)"),
      render: (d) => <Line text={`${prettyVolume(d.volume)}`} />,
    },
    {
      header: t("Lots"),
      className: colStyles.narrowColumn,
      render: (d) => <Line text={`${d.lots}`} />,
    },
    {
      header: t("Réd. GES"),
      className: colStyles.narrowColumn,
      render: (d) => <Line text={`${d.avg_ghg_reduction.toFixed(2)}%`} />,
    },
    padding,
  ]

  const inColumns: Column<SummaryItem>[] = [
    padding,
    {
      header: t("Fournisseur"),
      render: (d) => <Line text={d.entity || "N/A"} />,
    },
    ...columns,
  ]

  const outColumns: Column<SummaryItem>[] = [
    padding,
    {
      header: t("Client"),
      render: (d) => <Line text={d.entity || "N/A"} />,
    },
    ...columns,
  ]

  const allColumns: Column<SummaryItem>[] = [
    padding,
    {
      header: t("Fournisseur"),
      render: (d) => <Line text={d.vendor || "N/A"} />,
    },
    {
      header: t("Client"),
      render: (d) => <Line text={d.client || "N/A"} />,
    },
    ...columns,
  ]

  return (
    <Fragment>
      {isInEmpty && isOutEmpty && isAllEmpty && (
        <Alert level="warning" icon={AlertCircle}>
          <Trans>Aucune transaction trouvée pour cette période</Trans>
        </Alert>
      )}

      {!isInEmpty && (
        <Box className={styles.transactionSummary}>
          <Title className={styles.transactionSummarySection}>
            <Trans>Entrées</Trans>
            <span className={styles.transactionSummaryTotal}>
              <Trans count={totalIn.lots}>
                ▸ {{ count: totalIn.lots }} lots ▸{" "}
                {{ volume: prettyVolume(totalIn.volume) }} litres
              </Trans>
            </span>
          </Title>
          <Table columns={inColumns} rows={summaryInRows} />
        </Box>
      )}

      {!isOutEmpty && (
        <Box className={styles.transactionSummary}>
          <Title className={styles.transactionSummarySection}>
            <Trans>Sorties</Trans>
            <span className={styles.transactionSummaryTotal}>
              <Trans count={totalOut.lots}>
                ▸ {{ count: totalOut.lots }} lots ▸{" "}
                {{ volume: prettyVolume(totalOut.volume) }} litres
              </Trans>
            </span>
          </Title>
          <Table columns={outColumns} rows={summaryOutRows} />
        </Box>
      )}

      {!isAllEmpty && (
        <Box className={styles.transactionSummary}>
          <Title className={styles.transactionSummarySection}>
            <Trans>Transactions</Trans>
            <span className={styles.transactionSummaryTotal}>
              <Trans count={totalAll.lots}>
                ▸ {{ count: totalAll.lots }} lots ▸{" "}
                {{ volume: prettyVolume(totalAll.volume) }} litres
              </Trans>
            </span>
          </Title>
          <Table columns={allColumns} rows={summaryAllRows} />
        </Box>
      )}
    </Fragment>
  )
}

function summaryGetter(entity?: EntitySelection, isStock?: boolean) {
  if (isStock) return getStocksSummary

  switch (entity?.entity_type) {
    case EntityType.Administration:
      return getAdminSummary
    case EntityType.Auditor:
      return getAuditorSummary
    default:
      return getLotsSummary
  }
}

interface SummaryOptions {
  entity?: EntitySelection
  stock?: boolean
  short?: boolean
}

export function useSummary(
  query: TransactionQuery,
  selection: number[] | undefined,
  options: SummaryOptions = {}
) {
  const [summary, getSummary] = useAPI(
    summaryGetter(options.entity, options.stock)
  )

  useEffect(() => {
    getSummary(query, selection ?? [], options.short)
  }, [getSummary, query, selection, options.short])

  return summary
}

type SummaryPromptProps = PromptProps<number[]> & {
  title: string
  description: string
  readOnly?: boolean
  stock?: boolean
  entityID?: number
  selection?: number[]
  entity?: EntitySelection
  query: TransactionQuery
}

export const SummaryPrompt = ({
  stock,
  title,
  description,
  query,
  selection,
  readOnly,
  entity,
  onResolve,
}: SummaryPromptProps) => {
  const { t } = useTranslation()
  const summary = useSummary(query, selection, { stock, entity })

  return (
    <Dialog wide onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      {summary.data && (
        <TransactionSummary
          in={summary.data.in}
          out={summary.data.out}
          transactions={summary.data.transactions}
        />
      )}

      <DialogButtons>
        {!readOnly && (
          <Button
            level="primary"
            icon={Check}
            onClick={() => onResolve(summary.data?.tx_ids)}
          >
            <Trans>Confirmer</Trans>
          </Button>
        )}
        <Button icon={Return} onClick={() => onResolve()}>
          {readOnly ? t("Retour") : t("Annuler")}
        </Button>
      </DialogButtons>

      {summary.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default TransactionSummary
