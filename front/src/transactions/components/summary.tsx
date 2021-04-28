import { Fragment, useEffect } from "react"
import Table, { Column, Line } from "common/components/table"
import { SummaryItem, TransactionQuery } from "common/types"
import { padding, prettyVolume } from "./list-columns"
import { Alert } from "common/components/alert"
import { AlertCircle, Check } from "common/components/icons"

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
import * as api from "../api"
import { Button } from "common/components/button"

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
      {isInEmpty && isOutEmpty && (
        <Alert level="warning" icon={AlertCircle}>
          Aucune information trouvée pour la période donnée.
        </Alert>
      )}

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

      <br />

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
  filters: TransactionQuery | undefined,
  selection: number[] | undefined
) {
  const [summary, getSummary] = useAPI(api.getLotsSummary)

  useEffect(() => {
    if (typeof filters !== "undefined") {
      getSummary(filters, selection ?? [])
    }
  }, [getSummary, filters, selection])

  return summary
}

type SummaryPromptProps = PromptProps<boolean> & {
  title: string
  description: string
  stock?: boolean
  entityID?: number
  selection?: number[]
  filters?: TransactionQuery
}

export const SummaryPrompt = ({
  title,
  description,
  filters,
  selection,
  onResolve,
}: SummaryPromptProps) => {
  const summary = useSummary(filters, selection)

  return (
    <Dialog
      onResolve={onResolve}
      className={summary.data ? styles.dialogWide : undefined}
    >
      <DialogTitle text={title} />
      <DialogText text={description} />

      {summary.data && (
        <TransactionSummary in={summary.data.in} out={summary.data.out} />
      )}

      <DialogButtons>
        <Button level="primary" icon={Check} onClick={() => onResolve(true)}>
          OK
        </Button>
        <Button onClick={() => onResolve()}>Annuler</Button>
      </DialogButtons>

      {summary.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default TransactionSummary
