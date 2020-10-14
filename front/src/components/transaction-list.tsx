import React from "react"
import cl from "clsx"

import { Lots, LotStatus } from "../services/types"
import { StatusSelection, TransactionSelection, SortingSelection } from "../hooks/use-transactions" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import styles from "./transaction-list.module.css"

import {
  AlertCircle,
  Check,
  Cross,
  Rapport,
  Download,
  Upload,
  Plus,
} from "./system/icons"

import { Alert, Box, Button, LoaderOverlay } from "./system"
import Pagination from "./system/pagination"
import TransactionTable from "./transaction-table"
import { Link } from "./relative-route"

type DraftActionProps = {
  disabled: boolean
  selection: number
  onUpload: (f: File) => void
  onDelete: () => void
  onValidate: () => void
  onDeleteAll: () => void
  onValidateAll: () => void
}

const DraftLotsActions = ({
  disabled,
  selection,
  onUpload,
  onDelete,
  onValidate,
  onDeleteAll,
  onValidateAll,
}: DraftActionProps) => (
  <React.Fragment>
    <Button as="label" icon={Upload}>
      Importer fichier
      <input
        type="file"
        style={{ display: "none" }}
        onChange={(e) => onUpload(e!.target.files![0])}
      />
    </Button>

    <Link relative to="add">
      <Button icon={Plus} level="primary">
        Créer lot
      </Button>
    </Link>

    <Button
      icon={Check}
      level="success"
      disabled={disabled}
      onClick={selection > 0 ? onValidate : onValidateAll}
    >
      Envoyer {selection > 0 ? `sélection` : "tout"}
    </Button>

    <Button
      icon={Cross}
      level="danger"
      disabled={disabled}
      onClick={selection > 0 ? onDelete : onDeleteAll}
    >
      Supprimer {selection > 0 ? `sélection` : "tout"}
    </Button>
  </React.Fragment>
)

const ValidatedLotsActions = () => (
  <Link relative to="show-summary-out">
    <Button
      className={styles.transactionButtons}
      level="primary"
      icon={Rapport}
    >
      Rapport de sorties
    </Button>
  </Link>
)

const ActionBar = ({ children }: { children: React.ReactNode }) => (
  <Box row className={cl(styles.actionBar)}>
    {children}
  </Box>
)

type TransactionListProps = {
  transactions: ApiState<Lots>
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  pagination: PageSelection
  onUpload: (f: File) => void
  onDelete: (ids: number[]) => void
  onValidate: (ids: number[]) => void
  onDuplicate: (id: number) => void
  onExportAll: () => void
  onDeleteAll: () => void
  onValidateAll: () => void
}

const TransactionList = ({
  transactions,
  status,
  sorting,
  selection,
  pagination,
  onUpload,
  onDelete,
  onDuplicate,
  onValidate,
  onExportAll,
  onDeleteAll,
  onValidateAll,
}: TransactionListProps) => {
  const tx = transactions.data

  const isLoading = transactions.loading
  const isError = typeof transactions.error === "string"
  const isEmpty = tx === null || tx.lots.length === 0

  return (
    <Box className={styles.transactionList}>
      <ActionBar>
        <Button icon={Download} disabled={isEmpty} onClick={onExportAll}>
          Exporter tout
        </Button>

        {status.active === LotStatus.Draft && (
          <DraftLotsActions
            disabled={isEmpty}
            selection={selection.selected.length}
            onUpload={onUpload}
            onDelete={() => onDelete(selection.selected)}
            onValidate={() => onValidate(selection.selected)}
            onDeleteAll={onDeleteAll}
            onValidateAll={onValidateAll}
          />
        )}

        {status.active === LotStatus.Validated && <ValidatedLotsActions />}
      </ActionBar>

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
