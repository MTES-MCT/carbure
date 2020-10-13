import React from "react"
import cl from "clsx"

import { Lots, LotStatus } from "../services/types"
import { StatusSelection, TransactionSelection, SortingSelection } from "../hooks/use-transactions" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import styles from "./transaction-list.module.css"

import { Alert, Box, Button, LoaderOverlay } from "./system"
import { AlertCircle, Check, Cross, Rapport } from "./system/icons"
import Pagination from "./system/pagination"
import TransactionTable from "./transaction-table"
import { Link } from "./relative-route"

type DraftActionProps = {
  disabled: boolean
  onDelete: () => void
  onValidate: () => void
}

type ValidatedLotsActionProps = {

}

const DraftLotsActions = ({ disabled, onDelete, onValidate }: DraftActionProps) => (
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

const ValidatedLotsActions = ({}: ValidatedLotsActionProps) => (
  <Box row className={cl(styles.actionBar)}>
    <Link to="validated/show-summary-out">
      <Button
        className={styles.transactionButtons}
        level="primary"
        icon={Rapport}
      >
        Rapport de sorties
      </Button>
    </Link>
  </Box>
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
          {status.active === LotStatus.Draft && (
            <DraftLotsActions
              disabled={selection.selected.length === 0}
              onDelete={() => onDelete(selection.selected)}
              onValidate={() => onValidate(selection.selected)}
            />
          )}
          {status.active === LotStatus.Validated && (
            <ValidatedLotsActions />
          )}
          <Box>
            <TransactionTable
              status={status}
              transactions={tx!}
              selection={selection}
              sorting={sorting}
              onDuplicate={onDuplicate}
              onValidate={onValidate}
              onDelete={onDelete}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

export default TransactionList
