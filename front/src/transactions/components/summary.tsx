import { Fragment, useEffect } from "react"
import Table, { Column, Line } from "common/components/table"
import { SummaryItem, TransactionQuery } from "common/types"
import { padding } from "./list-columns"
import { Check } from "common/components/icons"

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
import { getStocksSummary } from "stocks/api"
import { getLotsSummary } from "transactions/api"

const COLUMNS: Column<SummaryItem>[] = [
  {
    header: "Biocarburant",
    render: (d) => <Line text={d.biocarburant} />,
  },
  {
    header: "Volume (litres)",
    render: (d) => <Line text={`${prettyVolume(d.volume)}`} />,
  },
  {
    header: "Lots",
    className: colStyles.narrowColumn,
    render: (d) => <Line text={`${d.lots}`} />,
  },
  {
    header: "Réd. GES",
    className: colStyles.narrowColumn,
    render: (d) => <Line text={`${d.avg_ghg_reduction.toFixed(2)}%`} />,
  },
  padding,
]

type TransactionSummaryProps = {
  in: SummaryItem[] | null
  out: SummaryItem[] | null
}

const TransactionSummary = (props: TransactionSummaryProps) => {
  const summaryInRows = (props.in ?? []).map((v) => ({ value: v }))
  const summaryOutRows = (props.out ?? []).map((v) => ({ value: v }))

  const isInEmpty = summaryInRows.length === 0
  const isOutEmpty = summaryOutRows.length === 0

  const totalIn = {
    volume: summaryInRows.reduce((t, r) => t + r.value.volume, 0),
    lots: summaryInRows.reduce((t, r) => t + r.value.lots, 0),
  }

  const totalOut = {
    volume: summaryOutRows.reduce((t, r) => t + r.value.volume, 0),
    lots: summaryOutRows.reduce((t, r) => t + r.value.lots, 0),
  }

  const inColumns: Column<SummaryItem>[] = [
    padding,
    {
      header: "Fournisseur",
      render: (d) => <Line text={d.entity || "N/A"} />,
    },
    ...COLUMNS,
  ]

  const outColumns: Column<SummaryItem>[] = [
    padding,
    {
      header: "Client",
      render: (d) => <Line text={d.entity || "N/A"} />,
    },
    ...COLUMNS,
  ]

  return (
    <Fragment>
      {!isInEmpty && (
        <Box className={styles.transactionSummary}>
          <Title className={styles.transactionSummarySection}>
            Entrées
            <span className={styles.transactionSummaryTotal}>
              {"▸"} {totalIn.lots} lot{totalIn.lots !== 1 && "s"}
              {" ▸ "}
              {prettyVolume(totalIn.volume)} litres
            </span>
          </Title>
          <Table columns={inColumns} rows={summaryInRows} />
        </Box>
      )}

      {!isOutEmpty && (
        <Box className={styles.transactionSummary}>
          <Title className={styles.transactionSummarySection}>
            Sorties
            <span className={styles.transactionSummaryTotal}>
              {"▸"} {totalOut.lots} lot{totalOut.lots !== 1 && "s"}
              {" ▸ "}
              {prettyVolume(totalOut.volume)} litres
            </span>
          </Title>
          <Table columns={outColumns} rows={summaryOutRows} />
        </Box>
      )}
    </Fragment>
  )
}

export function useSummary(
  query: TransactionQuery,
  selection: number[] | undefined,
  stock?: boolean
) {
  const [summary, getSummary] = useAPI(
    stock ? getStocksSummary : getLotsSummary
  )

  useEffect(() => {
    getSummary(query, selection ?? [])
  }, [getSummary, query, selection])

  return summary
}

type SummaryPromptProps = PromptProps<number[]> & {
  title: string
  description: string
  stock?: boolean
  entityID?: number
  selection?: number[]
  query: TransactionQuery
}

export const SummaryPrompt = ({
  stock,
  title,
  description,
  query,
  selection,
  onResolve,
}: SummaryPromptProps) => {
  const summary = useSummary(query, selection, stock)

  return (
    <Dialog wide onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      {summary.data && (
        <TransactionSummary in={summary.data.in} out={summary.data.out} />
      )}

      <DialogButtons>
        <Button
          level="primary"
          icon={Check}
          onClick={() => onResolve(summary.data?.tx_ids)}
        >
          Confirmer
        </Button>
        <Button onClick={() => onResolve()}>Annuler</Button>
      </DialogButtons>

      {summary.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default TransactionSummary
