import React from "react"
import cl from "clsx"

import { Lots, LotStatus } from "../services/types"
import { StatusSelection, TransactionSelection, SortingSelection } from "../hooks/use-transactions" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import styles from "./transaction-list.module.css"

import { Alert, Box, Button, Table, LoaderOverlay } from "./system"
import { AlertCircle, Check, ChevronRight, Copy, Cross } from "./system/icons"
import Pagination from "./system/pagination"
import { TransactionRow, TransactionRowContainer } from "./transaction-row"

// valeurs acceptables pour le sort_by: ['period', 'client', 'biocarburant', 'matiere_premiere', 'ghg_reduction', 'volume', 'pays_origine']

const COLUMNS = [
  { key: "", label: "Statut" },
  { key: "period", label: "Date d'ajout" },
  { key: "", label: "N° Douane" },
  { key: "client", label: "Client" },
  { key: "biocarburant", label: "Biocarburant" },
  { key: "pays_origine", label: "Provenance" },
  { key: "", label: "Destination" },
  { key: "matiere_premiere", label: "Mat. Première" },
  { key: "ghg_reduction", label: "Économie" },
]

function stopProp(handler: Function = () => {}) {
  return (e: React.SyntheticEvent) => {
    e.stopPropagation()
    handler()
  }
}

function isEverythingSelected(ids: number[], selected: number[]) {
  ids.sort()
  selected.sort()

  return (
    ids.length > 0 &&
    ids.length === selected.length &&
    selected.every((id, i) => ids[i] === id)
  )
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

type TxColumnsProps = {
  sorting: SortingSelection
  children: React.ReactNode
}

const TransactionColumns = ({ sorting, children }: TxColumnsProps) => (
  <thead>
    <tr>
      {children}
      {COLUMNS.map((column, i) => (
        <th key={i} onClick={() => sorting.sortBy(column.key)}>
          {column.label}
          {sorting.column && sorting.column === column.key && (
            <span>{sorting.order === "asc" ? " ▲" : " ▼"}</span>
          )}
        </th>
      ))}
      <th />
    </tr>
  </thead>
)

type DraftTableProps = {
  transactions: Lots
  selection: TransactionSelection
  sorting: SortingSelection
  onDelete: (ids: number[]) => void
  onValidate: (ids: number[]) => void
  onDuplicate: (id: number) => void
}

const DraftTable = ({
  transactions,
  sorting,
  selection,
  onDelete,
  onDuplicate,
  onValidate,
}: DraftTableProps) => {
  const ids = transactions ? transactions.lots.map((t) => t.id) : []

  const selectAllCheckbox = (
    <input
      type="checkbox"
      checked={isEverythingSelected(ids, selection.selected)}
      onChange={(e) => selection.selectMany(e.target.checked ? ids : [])}
    />
  )

  return (
    <Table className={styles.draftTransactionTable}>
      <TransactionColumns sorting={sorting}>
        <th>{selectAllCheckbox}</th>
      </TransactionColumns>

      <tbody>
        {transactions.lots.map((tx) => (
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
        ))}
      </tbody>
    </Table>
  )
}

type TxTableProps = {
  transactions: Lots
  sorting: SortingSelection
}

const TransactionTable = ({ transactions, sorting }: TxTableProps) => (
  <Table className={styles.transactionTable}>
    <TransactionColumns sorting={sorting}>
      <th /> {/* empty first column */}
    </TransactionColumns>

    <tbody>
      {transactions.lots.map((tx) => (
        <TransactionRowContainer key={tx.id} id={tx.id}>
          <td /> {/* empty first column */}
          <TransactionRow transaction={tx} />
          <td className={styles.actionColumn}>
            <ChevronRight className={styles.transactionArrow} />
          </td>
        </TransactionRowContainer>
      ))}
    </tbody>
  </Table>
)

type TransactionListProps = {
  transactions: ApiState<Lots>
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  pagination: PageSelection
  onDelete: (ids: number[]) => void
  onValidate: (ids: number[]) => void
  onDuplicate: (id: number) => void
}

const TransactionList = ({
  transactions,
  status,
  sorting,
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
              sorting={sorting}
              onDuplicate={onDuplicate}
              onValidate={onValidate}
              onDelete={onDelete}
            />
          ) : (
            <TransactionTable transactions={tx!} sorting={sorting} />
          )}

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

export default TransactionList
