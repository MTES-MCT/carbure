import React from "react"
import cl from "clsx"
import { useHistory } from "react-router-dom"

import { Transaction, Lots, LotStatus } from "../services/types"
import { TransactionSelection } from "../hooks/use-transactions"
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import styles from "./transaction-list.module.css"

import { getStatus } from "../services/lots"

import { Alert, Box, Button, LoaderOverlay, Table } from "./system"
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

const Actions = ({ disabled, onDelete, onValidate }: ActionProps) => {
  return (
    <Box row className={cl(styles.actionBar)}>
      <Button
        disabled={disabled}
        icon={Check}
        level="primary"
        onClick={onValidate}
      >
        Valider la sélection
      </Button>
      <Button
        disabled={disabled}
        icon={Cross}
        level="danger"
        onClick={onDelete}
      >
        Supprimer la sélection
      </Button>
    </Box>
  )
}

type TransactionRowProps = {
  transaction: Transaction
  selected: boolean
  onDelete: () => void
  onDuplicate: () => void
  onValidate: () => void
  onSelect: () => void
}

const TransactionRow = ({
  transaction: tx,
  selected,
  onDelete,
  onDuplicate,
  onValidate,
  onSelect,
}: TransactionRowProps) => {
  const history = useHistory()

  return (
    <tr
      className={styles.transactionRow}
      onClick={() => history.push(`/transactions/${tx.id}`)}
    >
      <td>
        <input
          type="checkbox"
          checked={selected}
          onChange={onSelect}
          onClick={stopProp()}
        />
      </td>

      <td>
        <Status value={getStatus(tx)} />
      </td>

      <td>
        <Line text={tx.lot.period} />
      </td>

      <td>
        <Line text={tx.dae} />
      </td>

      <td>
        <Line text={tx.carbure_client?.name ?? tx.unknown_client ?? ""} />
      </td>

      <td>
        <TwoLines top={tx.lot.biocarburant.name} bottom={`${tx.lot.volume}L`} />
      </td>

      <td>
        <TwoLines
          top={tx.lot.carbure_producer?.name ?? tx.lot.unknown_producer}
          bottom={
            tx.lot.carbure_production_site?.country.name ??
            tx.lot.unknown_production_country
          }
        />
      </td>

      <td>
        <TwoLines
          top={tx.carbure_delivery_site?.city ?? tx.unknown_delivery_site ?? ""}
          bottom={
            tx.carbure_delivery_site?.country.name ??
            tx.unknown_delivery_site_country?.name
          }
        />
      </td>

      <td>
        <TwoLines
          top={tx.lot.matiere_premiere.name}
          bottom={tx.lot.pays_origine.name}
        />
      </td>

      <td>
        <Line text={`${tx.lot.ghg_reduction}%`} />
      </td>

      <td className={styles.actionColumn}>
        <ChevronRight className={styles.transactionArrow} />

        <div className={styles.transactionActions}>
          <Copy title="Dupliquer le lot" onClick={stopProp(onDuplicate)} />
          <Check title="Envoyer le lot" onClick={stopProp(onValidate)} />
          <Cross title="Supprimer le lot" onClick={stopProp(onDelete)} />
        </div>
      </td>
    </tr>
  )
}

type TransactionListProps = {
  transactions: ApiState<Lots>
  pagination: PageSelection
  selection: TransactionSelection
  onDelete: (ids: number[]) => void
  onValidate: (ids: number[]) => void
  onDuplicate: (id: number) => void
}

const TransactionList = ({
  transactions,
  selection,
  pagination,
  onDelete,
  onDuplicate,
  onValidate,
}: TransactionListProps) => {
  const tx = transactions.data
  const ids = tx ? tx.lots.map((t) => t.id) : []

  const isLoading = transactions.loading
  const isError = typeof transactions.error === "string"
  const isEmpty = tx === null || tx.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      {isLoading && <LoaderOverlay />}

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
          <Actions
            disabled={selection.selected.length === 0}
            onDelete={() => onDelete(selection.selected)}
            onValidate={() => onValidate(selection.selected)}
          />

          <Table
            columns={COLUMNS}
            rows={tx!.lots}
            onSelectAll={(e) => selection.selectMany(e, ids)}
          >
            {(tx) => (
              <TransactionRow
                key={tx.id}
                transaction={tx}
                selected={selection.has(tx.id)}
                onSelect={() => selection.selectOne(tx.id)}
                onDuplicate={() => onDuplicate(tx.id)}
                onValidate={() => onValidate([tx.id])}
                onDelete={() => onDelete([tx.id])}
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
