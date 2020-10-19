import React from "react"
import cl from "clsx"

import { Lots, LotStatus } from "../services/types"
import { SortingSelection } from "../hooks/use-transactions" // prettier-ignore

import styles from "./transaction-table.module.css"

import { Table } from "./system"
import { Check, ChevronRight, Copy, Cross } from "./system/icons"
import { TransactionRow, TransactionRowContainer, StockTransactionRow } from "./transaction-row"
import { TransactionSelection } from "../hooks/query/use-selection"
import { StatusSelection } from "../hooks/query/use-status"

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

const STOCK_COLUMNS = [
  { key: "carbure_id", label: "ID" },
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

function hasErrors(transactions: Lots, id: number): boolean {
  return (
    transactions.lots_errors[id]?.length > 0 ||
    transactions.tx_errors[id]?.length > 0
  )
}

type DisplayTableProps = {
  transactions: Lots
  sorting: SortingSelection
}

const DisplayTable = ({ transactions, sorting }: DisplayTableProps) => (
  <Table className={styles.transactionTable}>
    <TransactionColumns sorting={sorting}>
      <th />
    </TransactionColumns>

    <tbody>
      {transactions.lots.map((tx) => (
        <TransactionRowContainer
          key={tx.id}
          id={tx.id}
          error={hasErrors(transactions, tx.id)}
        >
          <td />
          <TransactionRow transaction={tx} />
          <td className={styles.actionColumn}>
            <ChevronRight className={styles.transactionArrow} />
          </td>
        </TransactionRowContainer>
      ))}
    </tbody>
  </Table>
)

type ActionTableProps = {
  transactions: Lots
  selection: TransactionSelection
  sorting: SortingSelection
  onDelete: (id: number) => void
  onValidate: (id: number) => void
  onDuplicate: (id: number) => void
}

const ActionTable = ({
  transactions,
  sorting,
  selection,
  onDelete,
  onDuplicate,
  onValidate,
}: ActionTableProps) => {
  const ids = transactions ? transactions.lots.map((t) => t.id) : []

  const selectAllCheckbox = (
    <input
      type="checkbox"
      checked={isEverythingSelected(ids, selection.selected)}
      onChange={(e) => selection.selectMany(e.target.checked ? ids : [])}
    />
  )

  return (
    <Table className={cl(styles.transactionTable, styles.actionTable)}>
      <TransactionColumns sorting={sorting}>
        <th>{selectAllCheckbox}</th>
      </TransactionColumns>

      <tbody>
        {transactions.lots.map((tx) => (
          <TransactionRowContainer
            key={tx.id}
            id={tx.id}
            error={hasErrors(transactions, tx.id)}
          >
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
                  onClick={stopProp(() => onValidate(tx.id))}
                />
                <Cross
                  title="Supprimer le lot"
                  onClick={stopProp(() => onDelete(tx.id))}
                />
              </div>
            </td>
          </TransactionRowContainer>
        ))}
      </tbody>
    </Table>
  )
}

type TransactionTableProps = {
  transactions: Lots
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  onDelete: (id: number) => void
  onValidate: (id: number) => void
  onDuplicate: (id: number) => void
}

export const TransactionTable = ({
  transactions,
  status,
  sorting,
  selection,
  onDelete,
  onDuplicate,
  onValidate,
}: TransactionTableProps) => {
  // return Display table for transactions that aren't drafts
  if (status.active !== LotStatus.Draft) {
    return <DisplayTable transactions={transactions} sorting={sorting} />
  }

  return (
    <ActionTable
      transactions={transactions}
      selection={selection}
      sorting={sorting}
      onDuplicate={onDuplicate}
      onValidate={onValidate}
      onDelete={onDelete}
    />
  )
}

type StockTableProps = {
  transactions: Lots
  sorting: SortingSelection
}

export const StockTable = ({
  transactions,
  sorting,
}: StockTableProps) => {
  return <DisplayStockTable transactions={transactions} sorting={sorting} />
}

const StockTransactionColumns = ({ sorting, children }: TxColumnsProps) => (
  <thead>
    <tr>
      {children}
      {STOCK_COLUMNS.map((column, i) => (
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

const DisplayStockTable = ({ transactions, sorting }: DisplayTableProps) => (
  <Table>
    <StockTransactionColumns sorting={sorting}>
      <th />
    </StockTransactionColumns>

    <tbody>
      {transactions.lots.map((tx) => (
        <TransactionRowContainer
          key={tx.id}
          id={tx.id}
          error={hasErrors(transactions, tx.id)}
        >
          <td />
          <StockTransactionRow transaction={tx} />
          <td className={styles.actionColumn}>
            <ChevronRight className={styles.transactionArrow} />
          </td>
        </TransactionRowContainer>
      ))}
    </tbody>
  </Table>
)