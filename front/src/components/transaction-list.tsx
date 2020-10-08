import React from "react"
import cl from "clsx"

import { Lots, LotStatus, Transaction } from "../services/types"
import { StatusSelection, TransactionSelection } from "../hooks/use-transactions" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import styles from "./transaction-list.module.css"

import { Alert, Box, Button, Table, LoaderOverlay } from "./system"
import { AlertCircle, Check, ChevronRight, Copy, Cross } from "./system/icons"
import Pagination from "./system/pagination"
import { TransactionRow, TransactionRowContainer } from "./transaction-row"

// valeurs acceptables pour le sort_by: ['period', 'client', 'biocarburant', 'matiere_premiere', 'ghg_reduction', 'volume', 'pays_origine']

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

function stopProp(handler: Function = () => {}) {
  return (e: React.SyntheticEvent) => {
    e.stopPropagation()
    handler()
  }
}

type ActionProps = {
  disabled: boolean
  onDelete: () => void
  onValidate: () => void
}

const Actions = ({ disabled, onDelete, onValidate }: ActionProps) => (
  <Box row className={cl(styles.actionBar)}>
    <Button
      disabled={disabled}
      icon={Check}
      level="primary"
      onClick={onValidate}
    >
      Valider la sélection
    </Button>
    <Button disabled={disabled} icon={Cross} level="danger" onClick={onDelete}>
      Supprimer la sélection
    </Button>
  </Box>
)

function isEverythingSelected(ids: number[], selected: number[]) {
  ids.sort()
  selected.sort()

  return (
    ids.length > 0 &&
    ids.length === selected.length &&
    selected.every((id, i) => ids[i] === id)
  )
}

type DraftTableProps = {
  transactions: Lots
  selection: TransactionSelection
  onDelete: (ids: number[]) => void
  onValidate: (ids: number[]) => void
  onDuplicate: (id: number) => void
}

const DraftTable = ({
  transactions: tx,
  selection,
  onDelete,
  onDuplicate,
  onValidate,
}: DraftTableProps) => {
  const ids = tx ? tx.lots.map((t) => t.id) : []

  const selectAllCheckbox = (
    <input
      type="checkbox"
      checked={isEverythingSelected(ids, selection.selected)}
      onChange={(e) => selection.selectMany(e.target.checked ? ids : [])}
    />
  )

  return (
    <Table
      columns={[selectAllCheckbox, ...COLUMNS]}
      rows={tx!.lots}
      className={styles.draftTransactionTable}
    >
      {(tx) => (
        <TransactionRowContainer key={tx.id} id={tx.id}>
          <td>
            <input
              type="checkbox"
              checked={selection.has(tx.id)}
              onChange={() => selection.selectOne(tx.id)}
              onClick={stopProp()}
            />
          </td>

          <TransactionRow transaction={tx} />

          <td className={styles.actionColumn}>
            <ChevronRight className={styles.transactionArrow} />

            <div className={styles.transactionActions}>
              <Copy
                title="Dupliquer le lot"
                onClick={stopProp(() => onDuplicate(tx.id))}
              />
              <Check
                title="Envoyer le lot"
                onClick={stopProp(() => onValidate([tx.id]))}
              />
              <Cross
                title="Supprimer le lot"
                onClick={stopProp(() => onDelete([tx.id]))}
              />
            </div>
          </td>
        </TransactionRowContainer>
      )}
    </Table>
  )
}

const TransactionTable = ({ transactions: tx }: { transactions: Lots }) => (
  <Table
    columns={[null, ...COLUMNS]}
    rows={tx!.lots}
    className={styles.transactionTable}
  >
    {(tx) => (
      <TransactionRowContainer key={tx.id} id={tx.id}>
        <td />

        <TransactionRow transaction={tx} />

        <td className={styles.actionColumn}>
          <ChevronRight className={styles.transactionArrow} />
        </td>
      </TransactionRowContainer>
    )}
  </Table>
)

type TransactionListProps = {
  transactions: ApiState<Lots>
  status: StatusSelection
  selection: TransactionSelection
  pagination: PageSelection
  onDelete: (ids: number[]) => void
  onValidate: (ids: number[]) => void
  onDuplicate: (id: number) => void
}

const TransactionList = ({
  transactions,
  status,
  selection,
  pagination,
  onDelete,
  onDuplicate,
  onValidate,
}: TransactionListProps) => {
  const tx = transactions.data

  const isLoading = transactions.loading
  const isError = typeof transactions.error === "string"
  const isEmpty = tx === null || tx.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      {isLoading && <LoaderOverlay />}

      {status.active === LotStatus.Draft && (
        <Actions
          disabled={selection.selected.length === 0}
          onDelete={() => onDelete(selection.selected)}
          onValidate={() => onValidate(selection.selected)}
        />
      )}

      {isError && (
        <Alert level="error">
          <AlertCircle />
          {transactions.error}
        </Alert>
      )}

      {!isError && isEmpty && (
        <Alert level="warning">
          <AlertCircle />
          Aucune transaction trouvée pour ces paramètres
        </Alert>
      )}

      {!isError && !isEmpty && (
        <React.Fragment>
          {status.active === LotStatus.Draft ? (
            <DraftTable
              transactions={tx!}
              selection={selection}
              onDuplicate={onDuplicate}
              onValidate={onValidate}
              onDelete={onDelete}
            />
          ) : (
            <TransactionTable transactions={tx!} />
          )}

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

export default TransactionList
