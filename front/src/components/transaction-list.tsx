import React from "react"
import cl from "clsx"
import { useHistory } from "react-router-dom"

import { Transaction, Lots, LotStatus } from "../services/types"
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import styles from "./transaction-list.module.css"

import { getStatus } from "../services/lots"

import { Alert, Box, LoaderOverlay, Table } from "./system"
import { AlertCircle, Check, ChevronRight, Copy, Cross } from "./system/icons"
import Pagination from "./system/pagination"

const COLUMNS = [
  "Statut",
  "Date d'ajout",
  "N° Douane",
  "Client",
  "Biocarburant",
  "Provenance",
  "Destination",
  "Mat. Première",
  "Économie",
]

const STATUS = {
  [LotStatus.Draft]: "Brouillon",
  [LotStatus.Validated]: "Envoyé",
  [LotStatus.ToFix]: "À corriger",
  [LotStatus.Accepted]: "Accepté",
  [LotStatus.Weird]: "Problème",
}

const Status = ({ value }: { value: LotStatus }) => (
  <span
    className={cl(styles.status, {
      [styles.statusValidated]: value === LotStatus.Validated,
      [styles.statusToFix]: value === LotStatus.ToFix,
      [styles.statusAccepted]: value === LotStatus.Accepted,
    })}
  >
    {STATUS[value]}
  </span>
)

const Line = ({ text, small = false }: { text: string; small?: boolean }) => (
  <span title={text} className={cl(styles.rowLine, small && styles.extraInfo)}>
    {text}
  </span>
)

const TwoLines = ({ top, bottom }: { top: string; bottom: string }) => (
  <div className={styles.dualRow}>
    <Line text={top} />
    <Line small text={bottom} />
  </div>
)

type TransactionRowProps = {
  transaction: Transaction
  onDelete: (id: number) => void
  onDuplicate: (id: number) => void
}

const TransactionRow = ({
  transaction,
  onDelete,
  onDuplicate,
}: TransactionRowProps) => {
  const history = useHistory()

  function handleDuplicate(e: React.MouseEvent) {
    e.stopPropagation()
    onDuplicate(transaction.id)
  }

  function handleDelete(e: React.MouseEvent) {
    e.stopPropagation()
    onDelete(transaction.id)
  }

  return (
    <tr
      className={styles.transactionRow}
      onClick={() => history.push(`/transactions/${transaction.id}`)}
    >
      <td>
        <input type="checkbox" name={transaction.dae} />
      </td>

      <td>
        <Status value={getStatus(transaction)} />
      </td>

      <td>
        <Line text={transaction.lot.period} />
      </td>

      <td>
        <Line text={transaction.dae} />
      </td>

      <td>
        <Line
          text={
            transaction.carbure_client?.name ?? transaction.unknown_client ?? ""
          }
        />
      </td>

      <td>
        <TwoLines
          top={transaction.lot.biocarburant.name}
          bottom={`${transaction.lot.volume}L`}
        />
      </td>

      <td>
        <TwoLines
          top={
            transaction.lot.carbure_producer?.name ??
            transaction.lot.unknown_producer
          }
          bottom={
            transaction.lot.carbure_production_site?.country.name ??
            transaction.lot.unknown_production_country
          }
        />
      </td>

      <td>
        <TwoLines
          top={
            transaction.carbure_delivery_site?.city ??
            transaction.unknown_delivery_site ??
            ""
          }
          bottom={
            transaction.carbure_delivery_site?.country.name ??
            transaction.unknown_delivery_site_country?.name
          }
        />
      </td>

      <td>
        <TwoLines
          top={transaction.lot.matiere_premiere.name}
          bottom={transaction.lot.pays_origine.name}
        />
      </td>

      <td>
        <Line text={`${transaction.lot.ghg_reduction}%`} />
      </td>

      <td className={styles.actionColumn}>
        <ChevronRight className={styles.transactionArrow} />

        <div className={styles.transactionActions}>
          <Copy title="Dupliquer le lot" onClick={handleDuplicate} />
          <Check title="Valider le lot" />
          <Cross title="Supprimer le lot" onClick={handleDelete} />
        </div>
      </td>
    </tr>
  )
}

type TransactionListProps = {
  transactions: ApiState<Lots>
  pagination: PageSelection
  onDelete: (id: number) => void
  onDuplicate: (id: number) => void
}

const TransactionList = ({
  transactions,
  pagination,
  onDelete,
  onDuplicate,
}: TransactionListProps) => {
  const tx = transactions.data

  const isLoading = transactions.loading
  const isError = typeof transactions.error === "string"
  const isEmpty = tx === null || tx.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      {isLoading && <LoaderOverlay />}

      {isError && (
        <Alert kind="error">
          <AlertCircle />
          {transactions.error}
        </Alert>
      )}

      {!isError && isEmpty && (
        <Alert kind="warning">
          <AlertCircle />
          Aucune transaction trouvée pour ces paramètres
        </Alert>
      )}

      {!isError && !isEmpty && (
        <React.Fragment>
          <Table columns={COLUMNS} rows={tx!.lots}>
            {(transaction) => (
              <TransactionRow
                key={transaction.id}
                transaction={transaction}
                onDelete={onDelete}
                onDuplicate={onDuplicate}
              />
            )}
          </Table>

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

export default TransactionList
