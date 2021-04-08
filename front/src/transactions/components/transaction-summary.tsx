import { Fragment } from "react"
import Table, { Column, Line } from "common/components/table"
import { SummaryItem } from "common/types"
import { padding } from "./list-columns"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"

import { Box, Title } from "common/components"
import styles from "./transaction-summary.module.css"
import colStyles from "./list-columns.module.css"

const COLUMNS: Column<SummaryItem>[] = [
  {
    header: "Biocarburant",
    render: (d) => <Line text={d.biocarburant} />,
  },
  {
    header: "Volume (litres)",
    render: (d) => <Line text={`${d.volume}`} />,
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
          <Title className={styles.transactionSummarySection}>Entrées</Title>
          <Table columns={inColumns} rows={summaryInRows} />
        </Box>
      )}

      <br />

      {!isOutEmpty && (
        <Box className={styles.transactionSummary}>
          <Title className={styles.transactionSummarySection}>Sorties</Title>
          <Table columns={outColumns} rows={summaryOutRows} />
        </Box>
      )}
    </Fragment>
  )
}

export default TransactionSummary
