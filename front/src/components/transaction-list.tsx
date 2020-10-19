import React from "react"
import cl from "clsx"

import { Lots, LotStatus } from "../services/types"
import { SortingSelection } from "../hooks/use-transactions" // prettier-ignore
import { PageSelection } from "./system/pagination"
import { ApiState } from "../hooks/helpers/use-api"

import { LotGetter } from "../hooks/transactions/use-get-lots"
import { LotUploader } from "../hooks/actions/use-upload-file"
import { LotDeleter } from "../hooks/actions/use-delete-lots"
import { LotValidator } from "../hooks/actions/use-validate-lots"
import { LotDuplicator } from "../hooks/actions/use-duplicate-lots"
import { StatusSelection } from "../hooks/query/use-status"
import { TransactionSelection } from "../hooks/query/use-selection"

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

import { Alert, AsyncButton, Box, Button, LoaderOverlay } from "./system"
import Pagination from "./system/pagination"
import { TransactionTable, StockTable } from "./transaction-table"
import { Link } from "./relative-route"


type DraftActionProps = {
  disabled: boolean
  hasSelection: boolean
  uploader: LotUploader
  deleter: LotDeleter
  validator: LotValidator
}

const DraftLotsActions = ({
  disabled,
  hasSelection,
  uploader,
  deleter,
  validator,
}: DraftActionProps) => {
  function onValidate() {
    if (hasSelection) {
      validator.validateSelection()
    } else {
      validator.validateAllDrafts()
    }
  }

  function onDelete() {
    if (hasSelection) {
      deleter.deleteSelection()
    } else {
      deleter.deleteAllDrafts()
    }
  }

  return (
    <React.Fragment>
      <AsyncButton as="label" icon={Upload} loading={uploader.loading}>
        Importer lots
        <input
          type="file"
          style={{ display: "none" }}
          onChange={(e) => uploader.uploadFile(e!.target.files![0])}
        />
      </AsyncButton>

      <Link relative to="add">
        <Button icon={Plus} level="primary">
          Créer lot
        </Button>
      </Link>

      <AsyncButton
        icon={Check}
        level="success"
        loading={validator.loading}
        disabled={disabled}
        onClick={onValidate}
      >
        Envoyer {hasSelection ? `sélection` : "tout"}
      </AsyncButton>

      <AsyncButton
        icon={Cross}
        level="danger"
        loading={deleter.loading}
        disabled={disabled}
        onClick={onDelete}
      >
        Supprimer {hasSelection ? `sélection` : "tout"}
      </AsyncButton>
    </React.Fragment>
  )
}

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
  transactions: LotGetter
  status: StatusSelection
  sorting: SortingSelection
  selection: TransactionSelection
  pagination: PageSelection
  deleter: LotDeleter
  uploader: LotUploader
  validator: LotValidator
  duplicator: LotDuplicator
}

export const TransactionList = ({
  transactions,
  status,
  sorting,
  selection,
  pagination,
  deleter,
  uploader,
  validator,
  duplicator,
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

      {!isError && (
        <ActionBar>
          <Button icon={Download} disabled={isEmpty} onClick={transactions.exportAllTransactions}>
            Exporter tout
          </Button>

          {status.active === LotStatus.Draft && (
            <DraftLotsActions
              disabled={isEmpty}
              hasSelection={selection.selected.length > 0}
              uploader={uploader}
              deleter={deleter}
              validator={validator}
            />
          )}

          {status.active === LotStatus.Validated && <ValidatedLotsActions />}
        </ActionBar>
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
              onDuplicate={duplicator.duplicateLot}
              onValidate={validator.validateLot}
              onDelete={deleter.deleteLot}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

type StockListProps = {
  transactions: ApiState<Lots>
  sorting: SortingSelection
  pagination: PageSelection
}

export const StockList = ({
  transactions,
  sorting,
  pagination,
}: StockListProps) => {
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
          <Box>
            <StockTable
              transactions={tx!}
              sorting={sorting}
            />
            {isLoading && <LoaderOverlay />}
          </Box>

          <Pagination pagination={pagination} total={tx!.total} />
        </React.Fragment>
      )}
    </Box>
  )
}

